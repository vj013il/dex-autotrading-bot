const crypto = require('crypto');

function encrypt(text, password) {
  const cipher = crypto.createCipher('aes-256-cbc', password);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return encrypted;
}

function decrypt(encrypted, password) {
  const decipher = crypto.createDecipher('aes-256-cbc', password);
  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

module.exports = { encrypt, decrypt };
