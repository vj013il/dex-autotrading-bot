// Using FPGA for price prediction
use fpga_driver::Fpga;

fn fpga_order_predictor(book: &OrderBook) -> (f64, f64) {
    let mut fpga = Fpga::connect("pcie:0");
    let input = book.to_fpga_buffer();
    let output = fpga.process(input); // Hardware calculation of best bid/ask
    (output.bid, output.ask)
}
