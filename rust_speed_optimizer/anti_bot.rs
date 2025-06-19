use rand::Rng;

fn generate_delay() -> u64 {
    rand::thread_rng().gen_range(100..500) // Random delay to avoid detection
}
