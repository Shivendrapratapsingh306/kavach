exports.getHome = (req, res) => {
  res.status(200).json({
    status: 'success',
    message: 'Welcome to Kavach Platform API',
    data: {
      version: '1.0.0'
    }
  });
};

exports.getHealth = (req, res) => {
  res.status(200).json({
    status: 'success',
    message: 'Server is healthy and running'
  });
};
