use std::collections::HashMap;

fn route_transaction(nodes: &HashMap<String, u64>, tx: &str) -> String {
    nodes.iter().min_by_key(|&(_, latency)| latency).unwrap().0.clone()
}
