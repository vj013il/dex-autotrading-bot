use std::fs::File;
use std::io::Write;

fn log_event(event: &str) {
    let mut file = File::create("log.txt").unwrap();
    file.write_all(event.as_bytes()).unwrap();
}
