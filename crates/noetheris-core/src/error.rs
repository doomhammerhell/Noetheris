use thiserror::Error;

pub type Result<T> = std::result::Result<T, NoetherisError>;

#[derive(Debug, Error)]
pub enum NoetherisError {
    #[error("invalid graph: {0}")]
    InvalidGraph(String),
    #[error("invalid qubo model: {0}")]
    InvalidQubo(String),
    #[error("invalid certificate: {0}")]
    InvalidCertificate(String),
    #[error("serialization failure: {0}")]
    Serialization(#[from] serde_json::Error),
    #[error("io failure: {0}")]
    Io(#[from] std::io::Error),
}
