class EmergencyStop {
public:
    void trigger() {
        for (auto& order : active_orders) {
            exchange.cancelOrder(order.id);
        }
        close_all_positions();
    }
};
