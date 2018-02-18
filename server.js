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

app.get('/driver/:email', (req, res) => {
  res.render('driver.ejs', {mail: req.params.email});
})

app.get('/passenger/:email', (req, res) => {
  res.render('passenger.ejs', {mail: req.params.email});
})

app.post('/', (req, res) => {
  var driver_email = req.body.email;
  var password = req.body.password;
  var usertype = req.body.driver;

  if (usertype == "") {
  	db.collection('driver').findOne({email: driver_email}, (err, user) => {
	    if(err){
	      console.log(err);
	    }
	    if(user){
	      res.redirect('/driver/' + driver_email)
	    } else {
	      db.collection('driver').insertOne(
	      	{email: req.body.email , password: req.body.password}, (err, result) => {
	        if (err) return console.log(err)
	        console.log("driver Signup complete!")
	        res.redirect('/driver/' + driver_email)
	      })
	    }
  	})
  } 

  else {
  	db.collection('passenger').findOne({email: email}, (err, user) => {
	    if(err){
	      console.log(err);
	    }
	    if(user){
	      res.redirect('/driver/' + driver_email)
	    } else {
	      db.collection('passenger').insertOne(req.body, (err, result) => {
	        if (err) return console.log(err)
	        console.log("passenger Signup complete!")
	        res.redirect('/driver/' + driver_email) //change to passenger page later
	      })
	    }
  	})
  }

  // submit distance to db

	app.post("/distance", (req, res) => {
	  db.collection('driver').update(
	   { email: req.body.mail },
	   {
	   	'$set' : {
	      start: req.body.start,
	      destination: req.body.destination
	  	}
	   }
	  )
	  res.redirect('/driver/' + req.body.mail);
	});
	
	app.post("/passenger-submit", (req, res) => {
	  db.collection('passenger').update(
	   { email: req.body.mail },
	   {
	   	'$set' : {
	      start: req.body.start,
	      destination: req.body.destination
	  	}
	   }
	  )
	  res.redirect('/passenger/' + req.body.mail);
	});
  
})
