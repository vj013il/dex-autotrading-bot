function handleError(error, context) {
  console.error(`Error in ${context}: ${error.message}`);
  return { error: true, message: error.message };
}

module.exports = { handleError };
