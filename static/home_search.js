function search(searchtype){
    let searchquery = document.getElementById("searchquery").value;
    searchquery = searchquery.replace("%", "%25");
    searchquery = searchquery.replace("<", "%3C");
    searchquery = searchquery.replace(">", "%3E");
    searchquery = searchquery.replace("#", "%23");
    searchquery = searchquery.replace("{", "%7B");
    searchquery = searchquery.replace("}", "%7D");
    searchquery = searchquery.replace("|", "%7C");
    searchquery = searchquery.replace("\\", "%5C");
    searchquery = searchquery.replace("^", "%5E");
    searchquery = searchquery.replace("~", "%7E");
    searchquery = searchquery.replace("[", "%5B");
    searchquery = searchquery.replace("]", "%5D");
    searchquery = searchquery.replace("`", "%60");
    searchquery = searchquery.replace(";", "%3B");
    searchquery = searchquery.replace("/", "%2F");
    searchquery = searchquery.replace("?", "%3F");
    searchquery = searchquery.replace(":", "%3A");
    searchquery = searchquery.replace("@", "%40");
    searchquery = searchquery.replace("=", "%3D");
    searchquery = searchquery.replace("&", "%26");
    searchquery = searchquery.replace("$", "%24");
    window.location = "/find?type=" + searchtype + "&query=" + searchquery
}