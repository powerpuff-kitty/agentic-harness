//! Package-source parsing for future local and remote Agentic Harness registries.

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PackageRef {
    Official(String),
    Github { repository: String, path: Option<String> },
}

impl PackageRef {
    pub fn parse(input: &str) -> Result<Self, String> {
        if let Some(rest) = input.strip_prefix("github:") {
            if rest.is_empty() { return Err("github package reference is empty".into()); }
            let (repository, path) = match rest.split_once('#') {
                Some((repo, path)) if !repo.is_empty() && !path.is_empty() => (repo.to_string(), Some(path.to_string())),
                Some(_) => return Err("invalid github package reference".into()),
                None => (rest.to_string(), None),
            };
            return Ok(Self::Github { repository, path });
        }
        let name = input.strip_prefix("official:").unwrap_or(input);
        if name.is_empty() || name.contains('/') { return Err("invalid official package name".into()); }
        Ok(Self::Official(name.to_string()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_official_and_github_references() {
        assert_eq!(PackageRef::parse("observability").unwrap(), PackageRef::Official("observability".into()));
        assert_eq!(PackageRef::parse("github:acme/harness#packs/security").unwrap(), PackageRef::Github { repository: "acme/harness".into(), path: Some("packs/security".into()) });
    }
}
