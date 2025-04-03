function hideLoginButton(){
    let profileLink = document.getElementById("profileLink");
    let navigation = document.getElementById("navigation");
    iconBar.setAttribute("style", "display:none;");
    navigation.classList.remove("hide");
}