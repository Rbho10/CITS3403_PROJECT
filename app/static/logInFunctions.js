/*
Created javascript file
*/

<<<<<<< HEAD
function validInputs(){
    /*
    when user tries to log in with unfilled inputs raise alert
    not necessary, html can validate if required forms contain value
    */
    let username = document.forms["logIn"]["username"].value;
    let password = document.forms["logIn"]["password"].value;
    if (username == ""){
        alert("Username required.");
        return false;
    }
    if (password == ""){
        alert("Password required.")
        return false;
    }
    return true;
}

=======
>>>>>>> main
function validAlert(){
    /*
    when user tries to log in and both/either username or password does not align with those in database
    throw alert that both/either username and/or password are incorrect
    */
<<<<<<< HEAD
    /* 
    if (validInputs() != true){
        return false;
    }
    //don't use, unnecessary. we use built in html to validate that they have input in the username and password cases.
    */
    let usernameInput = document.forms["logIn"]["username"].value;
    let passwordInput = document.forms["logIn"]["password"].value;
    /*
    if (usernameInput is in database){
        let password = document.forms["username"]["password"].value; //use usernameInput to find username and compare listed password with password input
    }
    else {
        alert("Username not found. Please create account.") //or just automatically send user to the account creation page
        return false;
    }
    if (passwordInput !== password){
        alert("Incorrect password.")    
        return false;
        //optional implement, have a tracker for how many times account has tried to be accessed. and close attempts after a certain number of failures
            //optional implement, send an email to the associated email address of usernameInput 
    }
    return true;
    */
=======
    alert('Either username or password are incorrect.');
>>>>>>> main
}