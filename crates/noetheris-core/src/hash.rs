use crate::Result;
use serde::Serialize;
use sha2::{Digest, Sha256};

pub fn stable_problem_hash<T: Serialize>(problem: &T) -> Result<String> {
    let encoded = serde_json::to_vec(problem)?;
    let digest = Sha256::digest(encoded);
    Ok(format!("sha256:{}", hex::encode(digest)))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::BTreeMap;

    #[test]
    fn hash_is_stable_for_ordered_maps() {
        let mut value = BTreeMap::new();
        value.insert("a", 1_u64);
        value.insert("b", 2_u64);
        let first = stable_problem_hash(&value).unwrap();
        let second = stable_problem_hash(&value).unwrap();
        assert_eq!(first, second);
        assert!(first.starts_with("sha256:"));
    }
}
