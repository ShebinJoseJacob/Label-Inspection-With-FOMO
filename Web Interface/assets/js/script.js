
let switchCtn = document.querySelector("#switch-cnt");
let switchC1 = document.querySelector("#switch-c1");
let switchC2 = document.querySelector("#switch-c2");
let switchCircle = document.querySelectorAll(".switch__circle");
let switchBtn = document.querySelectorAll(".switch-btn");
let aContainer = document.querySelector("#a-container");
let bContainer = document.querySelector("#b-container");
let allButtons = document.querySelectorAll(".submit");

let getButtons = (e) => e.preventDefault()

let changeForm = (e) => {

    switchCtn.classList.add("is-gx");
    setTimeout(function(){
        switchCtn.classList.remove("is-gx");
    }, 1500)

    switchCtn.classList.toggle("is-txr");
    switchCircle[0].classList.toggle("is-txr");
    switchCircle[1].classList.toggle("is-txr");

    switchC1.classList.toggle("is-hidden");
    switchC2.classList.toggle("is-hidden");
    aContainer.classList.toggle("is-txl");
    bContainer.classList.toggle("is-txl");
    bContainer.classList.toggle("is-z200");
}

let mainF = (e) => {
    for (var i = 0; i < allButtons.length; i++)
        allButtons[i].addEventListener("click", getButtons );
    for (var i = 0; i < switchBtn.length; i++)
        switchBtn[i].addEventListener("click", changeForm)
}

window.addEventListener("load", mainF);

function getObjKeys(obj, value) {
    return Object.keys(obj).filter(key => obj[key] === value);
  }
  const firebaseConfig = {
    apiKey: "AIzaSyAqbi6Cud5CDw7bXJE6nCPNCvMECS08oOE",
    authDomain: "counter-77c7e.firebaseapp.com",
    databaseURL: "https://counter-77c7e-default-rtdb.firebaseio.com",
    projectId: "counter-77c7e",
    storageBucket: "counter-77c7e.appspot.com",
    messagingSenderId: "192592357928",
    appId: "1:192592357928:web:1abe3dbf9425a3f649e31d"
  };
firebase.initializeApp(firebaseConfig);



function start() {
    firebase.database().ref('Count_Start').update({
        Value:1
    });
}

var countRef = firebase.database().ref('Count');

countRef.on('value', function(snapshot) {
    val = snapshot.val()
    zeros = getObjKeys(val, 0)
    count = Object.keys(val)
    let nonzeros = count.filter(x => !zeros.includes(x));
    
    nonzeros.forEach(function (item, index) {
        div = '#Recent_' + item;
        $(div).show();
        value = '#Recent__' + item + '__Count'
        console.log(value)
        $(value).text(val[item])

        div = '#Current_' + item;
        $(div).show();
        value = '#Current__' + item + '__Count'
        console.log(value)
        $(value).text(val[item])
      });

});

function stop() {
    firebase.database().ref('Count_Start').update({
        Value:0
    });
}