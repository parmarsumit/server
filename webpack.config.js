//const webpack = require("webpack");
const path = require("path");

//const HtmlWebpackPlugin = require('html-webpack-plugin');
//const ExtractTextPlugin = require("extract-text-webpack-plugin");

let config = {
  mode: 'development',
  entry: "./src/index.js",
  output: {
    path: path.resolve(__dirname, "./build/app"),
    filename: "./web.bundle.js"
  },
  module: {
  /**
    rules: [
      {
        test: /\.css$/,
        use: ExtractTextPlugin.extract({
          fallback: "style-loader",
          use: "css-loader"
        })
      },{
         test: /\.(png|jpg|gif)$/,
         use: "file-loader"
      }
    ]
  **/
  },
  plugins: [
    //new HtmlWebpackPlugin({template: './public/index.html'})
    //new ExtractTextPlugin("./index.css"),
  ]
}

module.exports = config;
