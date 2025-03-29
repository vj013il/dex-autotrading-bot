// Fetch Pyth price in React
const { connection } = useConnection();
const [solPrice, setSolPrice] = useState<number>(0);

useEffect(() => {
  const pythAccount = getPythSOLUSDAccount();
  connection.getAccountInfo(pythAccount).then(info => {
    const price = parsePriceData(info.data).price;
    setSolPrice(price);
  });
}, []);
