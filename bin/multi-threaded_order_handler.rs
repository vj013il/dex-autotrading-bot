use std::thread;

fn process_orders(orders: Vec<Order>) {
    let handles: Vec<_> = orders.into_iter().map(|order| {
        thread::spawn(move || {
            exchange.send_order(order);
        })
    }).collect();
    
    for handle in handles {
        handle.join().unwrap();
    }
}
