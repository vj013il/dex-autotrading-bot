use log::{info, error};

pub fn init_logger() {
    env_logger::init();
}

#[macro_export]
macro_rules! log_info {
    ($($arg:tt)*) => {
        info!($($arg)*);
    };
}

#[macro_export]
macro_rules! log_error {
    ($($arg:tt)*) => {
        error!($($arg)*);
    };
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    init_logger();
    log_info!("Logger initialized");
    Ok(())
}
