const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
    app.use(
        '/api',
        createProxyMiddleware({
            target: 'http://localhost:8000',
            changeOrigin: true,
            ws: true,
            pathRewrite: {
                '^/api': '/api'
            },
            onProxyReq: (proxyReq, req, res) => {
                // Log outgoing requests
                console.log('Proxying request:', req.method, req.path);
            },
            onProxyRes: (proxyRes, req, res) => {
                // Log responses
                console.log('Received response:', proxyRes.statusCode, req.path);
            },
            onError: (err, req, res) => {
                console.error('Proxy Error:', err);
                res.status(500).json({
                    error: 'Proxy Error',
                    message: err.message
                });
            }
        })
    );
}; 