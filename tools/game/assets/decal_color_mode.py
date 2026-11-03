"""Exact source-pixel mask classification; runtime color fill is an adaptation."""
def classify(image):
 image=image.convert('RGBA');channels=image.split();mask=channels[3].point(lambda value:255 if value else 0);values=[]
 for channel in channels[:3]:values.append([i for i,count in enumerate(channel.histogram(mask))if count])
 constant=[v[0]for v in values]if all(len(v)==1 for v in values)else None
 mode='alpha_mask'if constant in[[0,0,0],[255,255,255]]else'authored_rgba'
 return dict(color_mode=mode,source_visible_constant_rgb=constant,color_mode_provenance='Exact visible-pixel RGB classification; alpha-mask chosen-color fill is an explicit renderer adaptation, native compositor formula unresolved.')
