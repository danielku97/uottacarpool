const express = require('express');
const request = require('request');
const bodyParser= require('body-parser');
const app = express();
const MongoClient = require('mongodb').MongoClient;
var url = "mongodb://admin:password@ds053146.mlab.com:53146/uotta-carpool"
var db;

app.use(express.static(__dirname + "/views/"));
app.set('view engine', 'ejs')
app.use(bodyParser.urlencoded({extended: true}))
app.use(bodyParser.json());
// connect to the database
MongoClient.connect(url, (err, database) => {
  if (err) return console.log(err)
  db = database
  app.listen(process.env.PORT || 8000, () => {
    console.log('listening on 8000')
  })
})

app.get('/', (req, res) => {
  res.render('index.ejs', {});
})

app.post('/', (req, res) => {
  var email = req.body.email;
  var password = req.body.password;
  var usertype = req.body.driver;

  if (usertype == "") {
  	db.collection('driver').findOne({email: email, password: password}, (err, user) => {
	    if(err){
	      console.log(err);
	    }
	    if(user){
	      res.send("user already exists");
	    } else {
	      db.collection('driver').insertOne(req.body, (err, result) => {
	        if (err) return console.log(err)
	        console.log("driver Signup complete!")
	        res.redirect('/');
	      })
	    }
  	})
  } 

  else {
  	db.collection('passenger').findOne({email: email, password: password}, (err, user) => {
	    if(err){
	      console.log(err);
	    }
	    if(user){
	      res.send("user already exists");
	    } else {
	      db.collection('passenger').insertOne(req.body, (err, result) => {
	        if (err) return console.log(err)
	        console.log("passenger Signup complete!")
	        res.redirect('/');
	      })
	    }
  	})
  }
  
})