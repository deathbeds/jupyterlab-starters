module.exports = {
  output: {
    clean: true,
  },
  devtool: 'source-map',
  module: {
    rules: [
      {
        test: /\.js$/,
        use: process.env.WITH_JS_COV
          ? ['@ephesoft/webpack.istanbul.loader']
          : [
              {
                loader: 'source-map-loader',
                options: {
                  filterSourceMappingUrl: (url, resourcePath) => {
                    if (resourcePath.includes('@jupyterlab/rendermime')) {
                      return false;
                    }
                    return true;
                  },
                },
              },
            ],
      },
      {
        test: /\.html$/,
        type: 'asset/resource',
      },
    ],
  },
};
