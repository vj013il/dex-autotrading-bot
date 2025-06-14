function formatNumber(value, decimals = 2) {
  return Number(value).toFixed(decimals);
}

module.exports = { formatNumber };
