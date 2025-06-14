const axios = require('axios');

const apiClient = axios.create({
  timeout: 10000,
});

module.exports = { apiClient };
