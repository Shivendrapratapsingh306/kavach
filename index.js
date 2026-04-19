const express = require('express');
const router = express.Router();
const indexController = require('../controllers/indexController');

// Home route
router.get('/', indexController.getHome);

// Health check route for Render
router.get('/health', indexController.getHealth);

module.exports = router;
