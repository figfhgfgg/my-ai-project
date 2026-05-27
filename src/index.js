/**
 * Greet utility function for the web application.
 * @param {string} name - Name of the person to greet.
 * @returns {string} Greeting message.
 */
function greet(name) {
  if (!name) {
    return 'Hello, Guest! Welcome to our web app.';
  }
  return `Hello, ${name}! Welcome to our web app.`;
}

// Export for Node.js testing environments
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
  module.exports = { greet };
}
