use parry3d::{
    math::{Pose, Rotation, Vector},
    query::{self, Ray, RayCast, ShapeCastOptions},
    shape::{Cuboid, TriMesh},
};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
#[serde(default)]
pub struct NativeCollisionDefinition {
    pub points: Vec<[f32; 3]>,
    pub triangles: Vec<NativeTriangle>,
    pub polygons: Vec<NativePolygon>,
    pub patches: Vec<NativePatch>,
    pub splines: Vec<NativeSpline>,
    pub source: serde_json::Value,
}
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct NativeTriangle {
    pub indices: [u32; 3],
    pub normal: [f32; 3],
    pub surface_id: u8,
}
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct NativePolygon {
    pub indices: Vec<u32>,
    pub surface_id: u8,
}
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct NativePatch {
    pub indices: [u32; 16],
    /// Retained serialized metadata; not proven native query-grid dimensions.
    pub subdivisions: [u32; 2],
    pub native_tail: u32,
    pub surface_id: u8,
}
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct NativeSpline {
    pub indices: [u32; 4],
    pub surface_id: u8,
}

#[derive(Clone, Copy, Debug)]
pub struct NativeGroundHit {
    pub height: f32,
    pub normal: [f32; 3],
    pub surface_id: u8,
}
#[derive(Debug)]
pub struct NativeCollisionWorld {
    mesh: TriMesh,
    walls: Option<TriMesh>,
    surfaces: Vec<u8>,
    pub triangle_count: usize,
    pub unresolved_spline_count: usize,
}
impl NativeCollisionDefinition {
    /// 8230AAA0: recovered cubic Bernstein basis; native iterative intersections
    /// are approximated separately by a triangle tessellation for Parry queries.
    // Keep source component indices and accumulation order visible in recovered equations.
    #[allow(clippy::needless_range_loop)]
    pub fn patch_point(&self, patch: &NativePatch, u: f32, v: f32) -> [f32; 3] {
        let b = |t: f32| {
            let t2 = t * t;
            let t3 = t2 * t;
            [
                1. - 3. * t + 3. * t2 - t3,
                3. * t - 6. * t2 + 3. * t3,
                3. * t2 - 3. * t3,
                t3,
            ]
        };
        let bu = b(u);
        let bv = b(v);
        let mut out = [0.; 3];
        for j in 0..4 {
            for i in 0..4 {
                let p = self.points[patch.indices[4 * j + i] as usize];
                for axis in 0..3 {
                    out[axis] += (bu[j] * bv[i]) * p[axis];
                }
            }
        }
        out
    }
}
impl NativeCollisionWorld {
    // Keep source component indices and accumulation order visible in recovered equations.
    #[allow(clippy::needless_range_loop)]
    pub fn new(def: &NativeCollisionDefinition) -> Result<Self, String> {
        let mut vertices: Vec<Vector> = def.points.iter().map(|p| Vector::from_array(*p)).collect();
        let mut indices = Vec::new();
        let mut surfaces = Vec::new();
        for triangle in &def.triangles {
            indices.push(triangle.indices);
            surfaces.push(triangle.surface_id);
        }
        for polygon in &def.polygons {
            for triangle in triangulate_polygon(&polygon.indices, &vertices)? {
                indices.push(triangle);
                surfaces.push(polygon.surface_id);
            }
        }
        for patch in &def.patches {
            if patch
                .indices
                .iter()
                .any(|i| *i as usize >= def.points.len())
            {
                return Err("Native patch point index out of range".into());
            }
            let [nu, nv] = patch_query_subdivisions(def, patch);
            let base = vertices.len() as u32;
            for u in 0..=nu {
                for v in 0..=nv {
                    vertices.push(Vector::from_array(def.patch_point(
                        patch,
                        u as f32 / nu as f32,
                        v as f32 / nv as f32,
                    )));
                }
            }
            for u in 0..nu {
                for v in 0..nv {
                    let a = base + u * (nv + 1) + v;
                    let b = a + nv + 1;
                    indices.extend([[a, b, a + 1], [b, b + 1, a + 1]]);
                    surfaces.extend([patch.surface_id; 2]);
                }
            }
        }
        // 8226F810: four original cubic controls become a vertical ruled
        // Bernstein patch. Native global824AF4C0 defaults400cm; rows step
        // down166.66667175cm, spanning sourceY+4m through sourceY−1m.
        for spline in &def.splines {
            if spline
                .indices
                .iter()
                .any(|i| *i as usize >= def.points.len())
            {
                return Err("Native spline point index out of range".into());
            }
            let base = vertices.len() as u32;
            for row in 0..=1 {
                for step in 0..=16 {
                    let t = step as f32 / 16.;
                    let t2 = t * t;
                    let t3 = t2 * t;
                    let b = [
                        1. - 3. * t + 3. * t2 - t3,
                        3. * t - 6. * t2 + 3. * t3,
                        3. * t2 - 3. * t3,
                        t3,
                    ];
                    let mut point = Vector::ZERO;
                    for i in 0..4 {
                        point += Vector::from_array(def.points[spline.indices[i] as usize]) * b[i];
                    }
                    point.y += 4. - row as f32 * 5.000000152587891;
                    vertices.push(point);
                }
            }
            for step in 0..16 {
                let a = base + step;
                let b = a + 17;
                indices.extend([[a, b, a + 1], [b, b + 1, a + 1]]);
                surfaces.extend([spline.surface_id; 2]);
            }
        }
        if indices
            .iter()
            .flatten()
            .any(|i| *i as usize >= vertices.len())
        {
            return Err("Native triangle point index out of range".into());
        }
        let mut valid = Vec::new();
        let mut valid_surfaces = Vec::new();
        let mut walls = Vec::new();
        for (triangle, surface) in indices.into_iter().zip(surfaces) {
            let normal = (vertices[triangle[1] as usize] - vertices[triangle[0] as usize])
                .cross(vertices[triangle[2] as usize] - vertices[triangle[0] as usize]);
            if normal.length_squared() < 1e-12 {
                continue;
            }
            // Query-purpose partition, not a recovered native surface-material flag.
            if normal.normalize().y.abs() < 0.65 {
                walls.push(triangle);
            }
            valid.push(triangle);
            valid_surfaces.push(surface);
        }
        let triangle_count = valid.len();
        let mesh = TriMesh::new(vertices.clone(), valid)
            .map_err(|e| format!("Native collision mesh: {e:?}"))?;
        let walls = if walls.is_empty() {
            None
        } else {
            Some(TriMesh::new(vertices, walls).map_err(|e| format!("Native wall mesh: {e:?}"))?)
        };
        Ok(Self {
            mesh,
            walls,
            surfaces: valid_surfaces,
            triangle_count,
            unresolved_spline_count: 0,
        })
    }
    pub fn ground(&self, point: [f32; 3], above: f32, below: f32) -> Option<NativeGroundHit> {
        let ray = Ray::new(
            Vector::new(point[0], point[1] + above, point[2]),
            Vector::NEG_Y,
        );
        let hit = self
            .mesh
            .cast_local_ray_and_get_normal(&ray, above + below, true)?;
        let mut normal = hit.normal;
        if normal.y < 0. {
            normal = -normal;
        }
        Some(NativeGroundHit {
            height: ray.origin.y - hit.time_of_impact,
            normal: normal.to_array(),
            surface_id: self
                .surfaces
                .get(hit.subshape as usize)
                .copied()
                .unwrap_or(0),
        })
    }
    /// Query-only swept oriented chassis; ordered velocity response remains Rust game logic.
    pub fn resolve_chassis(
        &self,
        state: &mut crate::VehicleState,
        p: &crate::Handling,
        old_position: [f32; 3],
    ) -> bool {
        let Some(walls) = &self.walls else {
            return false;
        };
        let rotation = Rotation::from_xyzw(
            state.orientation[0],
            state.orientation[1],
            state.orientation[2],
            state.orientation[3],
        );
        let center = rotation * Vector::new(0., (p.body_height + p.body_min_y) * 0.5, 0.);
        let shape = Cuboid::new(Vector::new(
            p.body_width * 0.5,
            (p.body_height - p.body_min_y) * 0.5,
            p.body_length * 0.5,
        ));
        let old = Vector::from_array(old_position);
        let end = Vector::from_array(state.position);
        let delta = end - old;
        let start_pose = Pose::from_parts(old + center, rotation);
        let mut collided = false;
        if delta.length_squared() > 1e-10 {
            if let Ok(Some(hit)) = query::cast_shapes(
                &start_pose,
                delta,
                &shape,
                &Pose::IDENTITY,
                Vector::ZERO,
                walls,
                ShapeCastOptions {
                    max_time_of_impact: 1.,
                    target_distance: 0.002,
                    stop_at_penetration: false,
                    ..Default::default()
                },
            ) {
                let normal = hit.normal2;
                if normal.dot(delta) < 0. {
                    state.position =
                        (old + delta * (hit.time_of_impact - 0.001).max(0.)).to_array();
                    reflect_velocity(&mut state.velocity, normal);
                    collided = true;
                }
            }
        }
        let pose = Pose::from_parts(Vector::from_array(state.position) + center, rotation);
        if let Ok(Some(contact)) = query::contact(&pose, &shape, &Pose::IDENTITY, walls, 0.) {
            if contact.dist < 0. {
                let normal = contact.normal2;
                state.position = (Vector::from_array(state.position)
                    + normal * (-contact.dist + 0.002))
                    .to_array();
                reflect_velocity(&mut state.velocity, normal);
                collided = true;
            }
        }
        collided
    }
}
// Reconstruction query approximation, not a recovered native grid setting.
// Cubic second derivatives are bounded by6*max(second control difference).
// Linear interpolation contributes <=.75*D/n² per axis; triangle interpolation
// of the bilinear grid contributes <=2.25*mixedDifference/(nu*nv).
fn patch_query_subdivisions(def: &NativeCollisionDefinition, patch: &NativePatch) -> [u32; 2] {
    const ERROR: f32 = 0.01; // At most1cm for each of the three bound contributions.
    let p = |row: usize, col: usize| {
        Vector::from_array(def.points[patch.indices[row * 4 + col] as usize])
    };
    let mut du = 0f32;
    let mut dv = 0f32;
    let mut mixed = 0f32;
    for row in 0..4 {
        for col in 0..2 {
            dv = dv.max((p(row, col) - 2. * p(row, col + 1) + p(row, col + 2)).length());
        }
    }
    for row in 0..2 {
        for col in 0..4 {
            du = du.max((p(row, col) - 2. * p(row + 1, col) + p(row + 2, col)).length());
        }
    }
    for row in 0..3 {
        for col in 0..3 {
            mixed = mixed.max(
                (p(row + 1, col + 1) - p(row + 1, col) - p(row, col + 1) + p(row, col)).length(),
            );
        }
    }
    let mut nu = (0.75 * du / ERROR).sqrt().ceil().max(1.) as u32;
    let mut nv = (0.75 * dv / ERROR).sqrt().ceil().max(1.) as u32;
    let cells = (2.25 * mixed / ERROR).ceil() as u64;
    while u64::from(nu) * u64::from(nv) < cells {
        if nu <= nv {
            nu *= 2;
        } else {
            nv *= 2;
        }
    }
    [nu, nv]
}
fn reflect_velocity(velocity: &mut [f32; 3], normal: Vector) {
    let mut v = Vector::from_array(*velocity);
    let closing = v.dot(normal);
    if closing < 0. {
        v -= normal * (closing * 1.4);
    }
    *velocity = v.to_array();
}

fn triangulate_polygon(indices: &[u32], points: &[Vector]) -> Result<Vec<[u32; 3]>, String> {
    if indices.iter().any(|i| *i as usize >= points.len()) {
        return Err("Native polygon point index out of range".into());
    }
    if indices.len() < 3 {
        return Ok(vec![]);
    }
    let mut normal = Vector::ZERO;
    for i in 0..indices.len() {
        normal +=
            points[indices[i] as usize].cross(points[indices[(i + 1) % indices.len()] as usize]);
    }
    let drop = if normal.x.abs() > normal.y.abs() && normal.x.abs() > normal.z.abs() {
        0
    } else if normal.y.abs() > normal.z.abs() {
        1
    } else {
        2
    };
    let project = |index: u32| {
        let p = points[index as usize];
        match drop {
            0 => [p.y, p.z],
            1 => [p.x, p.z],
            _ => [p.x, p.y],
        }
    };
    let cross = |a: [f32; 2], b: [f32; 2], c: [f32; 2]| {
        (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    };
    let area: f32 = (0..indices.len())
        .map(|i| {
            let a = project(indices[i]);
            let b = project(indices[(i + 1) % indices.len()]);
            a[0] * b[1] - a[1] * b[0]
        })
        .sum();
    let sign = area.signum();
    let mut polygon = indices.to_vec();
    let mut result = Vec::new();
    while polygon.len() > 3 {
        let mut ear = None;
        for i in 0..polygon.len() {
            let previous = (i + polygon.len() - 1) % polygon.len();
            let next = (i + 1) % polygon.len();
            let a = project(polygon[previous]);
            let b = project(polygon[i]);
            let c = project(polygon[next]);
            let orientation = cross(a, b, c) * sign;
            if orientation.abs() < 1e-7 {
                ear = Some((i, None));
                break;
            }
            if orientation < 0. {
                continue;
            }
            let contains = polygon.iter().enumerate().any(|(j, index)| {
                j != previous && j != i && j != next && {
                    let p = project(*index);
                    cross(a, b, p) * sign >= -1e-7
                        && cross(b, c, p) * sign >= -1e-7
                        && cross(c, a, p) * sign >= -1e-7
                }
            });
            if !contains {
                ear = Some((i, Some([polygon[previous], polygon[i], polygon[next]])));
                break;
            }
        }
        let Some((index, triangle)) = ear else {
            return Err(
                "Native polygon cannot be triangulated without crossing its boundary".into(),
            );
        };
        if let Some(triangle) = triangle {
            result.push(triangle);
        }
        polygon.remove(index);
    }
    if polygon.len() == 3 {
        result.push([polygon[0], polygon[1], polygon[2]]);
    }
    Ok(result)
}
