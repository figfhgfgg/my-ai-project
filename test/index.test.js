const { greet } = require('../src/index');

describe('Index Tests', () => {
  test('should return default guest greeting when name is empty', () => {
    expect(greet()).toBe('Hello, Guest! Welcome to our web app.');
  });

  test('should return custom greeting when name is provided', () => {
    expect(greet('Alice')).toBe('Hello, Alice! Welcome to our web app.');
  });
});
