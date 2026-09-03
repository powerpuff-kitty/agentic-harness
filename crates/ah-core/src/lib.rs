//! Core types shared by Agentic Harness crates.

pub const PACKAGE_FORMAT_VERSION: u32 = 1;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PackageKind {
    Template,
    Preset,
    Pack,
    Skill,
    Policy,
    Profile,
}

impl PackageKind {
    pub const fn directory(self) -> &'static str {
        match self {
            Self::Template => "templates",
            Self::Preset => "presets",
            Self::Pack => "packs",
            Self::Skill => "skills",
            Self::Policy => "policies",
            Self::Profile => "profiles",
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PackageSpec {
    pub kind: PackageKind,
    pub name: String,
    pub version: String,
}

impl PackageSpec {
    pub fn official_path(&self) -> String {
        format!("packages/{}/{}", self.kind.directory(), self.name)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn official_package_paths_are_stable() {
        let spec = PackageSpec { kind: PackageKind::Skill, name: "threat-model".into(), version: "0.1.0".into() };
        assert_eq!(spec.official_path(), "packages/skills/threat-model");
    }
}
