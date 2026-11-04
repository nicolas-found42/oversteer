// Verification-only AppKit policy. Rendering and game code remain unchanged.
// Godot's macOS startup explicitly activates its app, even for background launches.
#import <AppKit/AppKit.h>
#import <objc/runtime.h>

static void replace(Class cls, const char *name, IMP implementation) {
    SEL selector = sel_registerName(name);
    Method method = class_getInstanceMethod(cls, selector);
    if (!method) {
        fprintf(stderr, "Background window guard: missing %s\n", name);
        _Exit(78);
    }
    class_replaceMethod(cls, selector, implementation, method_getTypeEncoding(method));
}

static void no_activation(id self, SEL selector, ...) {}
static BOOL no_focus(id self, SEL selector, ...) { return NO; }
static IMP original_activation_policy;

static BOOL background_policy(id app, SEL selector, NSApplicationActivationPolicy requested) {
    return ((BOOL (*)(id, SEL, NSApplicationActivationPolicy))original_activation_policy)(
        app, selector, NSApplicationActivationPolicyProhibited);
}

static void show_without_focus(NSWindow *window, SEL selector, id sender) {
    [window orderFront:sender];
}

__attribute__((constructor)) static void install_background_policy(void) {
    @autoreleasepool {
        Class godot = objc_getClass("GodotApplication");
        if (!godot) {
            fprintf(stderr, "Background window guard: unsupported Godot application\n");
            _Exit(78);
        }
        replace(godot, "activateApplication", (IMP)no_activation);
        original_activation_policy = class_getMethodImplementation(
            [NSApplication class], @selector(setActivationPolicy:));
        replace([NSApplication class], "setActivationPolicy:", (IMP)background_policy);
        replace([NSApplication class], "activateIgnoringOtherApps:", (IMP)no_activation);
        replace([NSApplication class], "activate", (IMP)no_activation);
        replace([NSRunningApplication class], "activateWithOptions:", (IMP)no_focus);
        if (class_getInstanceMethod([NSRunningApplication class],
                sel_registerName("activateFromApplication:options:"))) {
            replace([NSRunningApplication class], "activateFromApplication:options:", (IMP)no_focus);
        }
        replace([NSWindow class], "makeKeyAndOrderFront:", (IMP)show_without_focus);
        replace([NSWindow class], "makeKeyWindow", (IMP)no_activation);
        replace([NSWindow class], "makeMainWindow", (IMP)no_activation);
        replace(objc_getClass("GodotWindow"), "canBecomeKeyWindow", (IMP)no_focus);
        replace(objc_getClass("GodotWindow"), "canBecomeMainWindow", (IMP)no_focus);
        [[[NSWorkspace sharedWorkspace] notificationCenter]
            addObserverForName:NSWorkspaceDidActivateApplicationNotification
            object:nil queue:nil usingBlock:^(NSNotification *note) {
                NSRunningApplication *app = note.userInfo[NSWorkspaceApplicationKey];
                if (app.processIdentifier == getpid()) {
                    fprintf(stderr, "BACKGROUND FOCUS VIOLATION\n");
                }
            }];
        fprintf(stderr, "Oversteer background window guard installed\n");
    }
}
