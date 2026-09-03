//! Reusable audit primitives for Agentic Harness.

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum AuditDimension {
    CodeQuality,
    Maintainability,
    Architecture,
    Testing,
    Security,
    Performance,
    DependencyHealth,
    Documentation,
    AgentDocs,
    Operations,
    DesignSystem,
}

impl AuditDimension {
    pub const fn key(self) -> &'static str {
        match self {
            Self::CodeQuality => "code_quality",
            Self::Maintainability => "maintainability",
            Self::Architecture => "architecture",
            Self::Testing => "testing",
            Self::Security => "security",
            Self::Performance => "performance",
            Self::DependencyHealth => "dependency_health",
            Self::Documentation => "documentation",
            Self::AgentDocs => "agent_docs",
            Self::Operations => "operations",
            Self::DesignSystem => "design_system",
        }
    }
}

pub fn clamp_score(value: i64) -> i64 {
    value.clamp(0, 100)
}

pub fn weighted_score(values: &[(i64, u32)]) -> i64 {
    let total_weight: u32 = values.iter().map(|(_, weight)| *weight).sum();
    if total_weight == 0 { return 0; }
    let sum: i64 = values.iter().map(|(score, weight)| score * i64::from(*weight)).sum();
    (sum / i64::from(total_weight)).clamp(0, 100)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn scores_are_clamped() {
        assert_eq!(clamp_score(120), 100);
        assert_eq!(clamp_score(-5), 0);
    }
}
