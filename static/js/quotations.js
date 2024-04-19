let customer_list_sort_by = 'asc'
let customer_list_sort_string = 'customer_name'
let invoice_list_sort_by = 'desc'
let invoice_list_sort_string = 'invoice_id'
function showLoader() {
    var overlay = document.getElementById('overlay');
    overlay.style.display = 'block';
}
function hideLoader() {
    var overlay = document.getElementById('overlay');
    overlay.style.display = 'none';
}
function removeFragment() {
    history.pushState("", document.title, window.location.pathname);
    console.log('rese')
}
function change_sort_customer_list(sort_string){
    if (customer_list_sort_string == sort_string){
        if (customer_list_sort_by == 'asc'){
            customer_list_sort_by = 'desc'
        } else {
            customer_list_sort_by = 'asc'
        }
    }
    customer_list_sort_string = sort_string
    load_customer_list(customer_list_sort_string);
}
async function load_customer_list(sort_string) {
    showLoader()
    let no_data_template = `Check full <button class="button" onClick="load_invoice_list('invoice_id')">Invoice List</button> here.
    <br>To add a performa for a new customer, first <button class="button" onClick="add_customer()">Add New Customer</button> and then add invoice to that customer.
    <br><br>No customers yet.`
    try {
        const response = await fetch(`/customer_details?sort=${sort_string}&sort_by=${customer_list_sort_by}`);
        if (!response.ok) {
            document.getElementById("main_content").innerHTML = no_data_template
            document.getElementById("logs_table").innerHTML= ``
            hideLoader()
        }
        let data = await response.json();
        if (data.length > 0){
            let customer_details_html = `Check full <button class="button" onClick="load_invoice_list('invoice_id', true)">Invoice List</button> here.
            <br>To add a performa for a new customer, first <button class="button" onClick="add_customer()">Add New Customer</button> and then add invoice to that customer.
            <br><br>
            <table>
                <tr>
                    <th class="inv_head" >Sr.</th>
                    <th class="inv_head" onClick=change_sort_customer_list('customer_name')>Customer Name</th>
                    <th class="inv_head" onClick=change_sort_customer_list('salesman_name')>Salesman Name</th>
                    <th class="inv_head" onClick=change_sort_customer_list('total_amount')>Total Amount</th>
                </tr>`
                for (let i=0; i<data.length;i++){
                    if (i % 2 == 0){
                        customer_details_html += `<tr class="light">`
                    }
                    else {
                        customer_details_html += `<tr class="dark">`
                    }
                    customer_details_html += `<td>` + (i+1) + `</td><td style="cursor:pointer;color:#1D3B86;" onClick="customer_data('`+ data[i]['primarykey'] + `','invoice_id')">`+ data[i]['customer_name'] + `</td><td>`+ data[i]['salesman_name'] + `</td><td class="right">`+ number_formater(data[i]['total_amount']) + `</td></tr>`
                }
            customer_details_html += `</table>`
            document.getElementById("main_content").innerHTML =customer_details_html
            document.getElementById("logs_table").innerHTML= ``
        } else {
            document.getElementById("main_content").innerHTML = no_data_template
            document.getElementById("logs_table").innerHTML= ``
        }
        hideLoader()
    } catch (error) {
        console.error('Error:', error);
        document.getElementById("main_content").innerHTML = no_data_template
        hideLoader()
    }
}
function change_sort_invoice_list(sort_string){
    if (invoice_list_sort_string == sort_string){
        if (invoice_list_sort_by == 'asc'){
            invoice_list_sort_by = 'desc'
        } else {
            invoice_list_sort_by = 'asc'
        }
    }
    invoice_list_sort_string = sort_string
    load_invoice_list(invoice_list_sort_string);
}
async function load_invoice_list(sort_string) {
    showLoader()
    let no_data_template = `<button class="button" onClick="load_customer_list('customer_name')">&#x2190 Back to customer list</button>
    <br><br>No customers yet.`
    try {
        const response = await fetch(`/invoice_details?sort=${sort_string}&sort_by=${invoice_list_sort_by}`);
        if (!response.ok) {
            document.getElementById("main_content").innerHTML = no_data_template
            hideLoader()
        }
        let data = await response.json();
        if (data.length > 0){

            let customer_details_html = `<button class="button" onClick="load_customer_list('customer_name')">&#x2190 Back to customer list</button>
            <br><br>
            <table>
                <tr>
                    <th>Sr.</th>
                    <th onClick="change_sort_invoice_list('invoice_id', false)">Invoice #</a></th>
                    <th onClick="change_sort_invoice_list('date', false)">Date</a></th>
                    <th onClick="change_sort_invoice_list('customer_name', false)">Customer Name</a></th>
                    <th onClick="change_sort_invoice_list('salesman_name', false)">Salesman Name</a></th>
                    <th>Prepared By</th>
                    <th onClick="change_sort_invoice_list('invoice_amount', false)">Amount</th>
                    </tr>`
                for (let i=0; i<data.length;i++){
                    if (i % 2 == 0){
                        customer_details_html += `<tr class="light">`
                    }
                    else {
                        customer_details_html += `<tr class="dark">`
                    }
                    customer_details_html += `
                    <td>` + (i+1) + `</td>
                    <td><a href="/invoice?view=invoice_manager&invoice_id=` + data[i]['invoice_id'] + `">` + data[i]['invoice_id'] + `</a></td>
                    <td>` + data[i]['date'] + `</td>
                    <td style="cursor:pointer;color:#1D3B86;" onClick="customer_data(`+ data[i]['customer_id'] + `,'invoice_id')">`+ data[i]['customer_name'] + `</td>
                    <td>` + data[i]['salesman_name'] + `</td>
                    <td>` + data[i]['user_name'] + `</td>
                    <td class="right">` + number_formater(data[i]['invoice_amount']) + `</td>
                    </tr>`
                }
            customer_details_html += `</table>`
            document.getElementById("main_content").innerHTML =customer_details_html
        }else {
            document.getElementById("main_content").innerHTML = no_data_template
        }
        hideLoader()
    } catch (error) {
        console.error('Error:', error);
        document.getElementById("main_content").innerHTML = no_data_template
        hideLoader()
    }
}
async function customer_data(customer_id, sort) {
    showLoader()
    customer_logs_load(customer_id);
    let no_data_template = `Error Occurred.`
    try {
        const response = await fetch(`/customer_details?customer_id=${customer_id}`);
        if (!response.ok) {
            document.getElementById("main_content").innerHTML = no_data_template
            hideLoader()
        }
        let data = await response.json();
        if (data){
            let customer_details_html = `<p style="text-decoration:none; font-size:small;cursor:pointer;color:#1D3B86;" onClick="load_customer_list('customer_name')">&#x2190 Back to customer list</p>
            <h6>Customer Name: ` + data['customer_name'] + ` | Salesman Name: `+ data['salesman_name'] + `</h6>
            <button class="button" onClick="add_invoice('` + data['primarykey'] + `', '`+ data['customer_name'] + `')">Add New Invoice</button>
            <a href="/invoice?view=update_customer&customer_id=` + data['primarykey'] + `"><button class="button">Update Customer Details</button></a>
            <button class="button" onClick="logs()" id="log_button">Hide Logs</button>
            <a href="/invoice_logs"><button class="button">Check Invoice Logs</button></a>
            <br><br>
            `
            if (data['total_amount']>0){
                customer_details_html += `<div id="customer_invoice_list">` + number_formater(data['total_amount']) + `</div>`
            } else {
                customer_details_html += `<div id="customer_invoice_list"></div>
                `
            }

            document.getElementById("main_content").innerHTML = customer_details_html
            if (sessionStorage.getItem("log_show") == "true"){
                document.getElementById("log_button").textContent = "Hide Logs";
                document.getElementById("logs_table").style.display = '';
            } else {
                document.getElementById("log_button").textContent = "Show Logs";
                document.getElementById("logs_table").style.display = 'none'
            }

            customer_invoice_list_load(customer_id,sort)

        }else {
            document.getElementById("main_content").innerHTML = no_data_template
        }
        hideLoader()
    } catch (error) {
        console.error('Error:', error);
        document.getElementById("main_content").innerHTML = no_data_template
        hideLoader()
    }

}
async function customer_invoice_list_load(customer_id, sort) {
    showLoader()
    let no_data_template = `No Invoices.`
    try {
        const response = await fetch(`/invoice_details?customer_id=${customer_id}&sort=${sort}&sort_by=desc`);
        if (!response.ok) {
            document.getElementById("customer_invoice_list").innerHTML = no_data_template
            hideLoader()
        }
        let data = await response.json();
        if (data){
            let total_amount = document.getElementById("customer_invoice_list").innerText
            let customer_invoice_list = `<table>
            <tr><th>Sr.</th><th>Invoice ID</th><th>Date</th><th>Payment Terms</th><th>Amount</th><th>Prepared By</th><th colspan="2">Actions</th></tr>`
            for (let i=0;i<data.length;i++){
                if (i % 2 == 0){
                    customer_invoice_list += `<tr class="light">`
                }
                else {
                    customer_invoice_list += `<tr class="dark">`
                }
                customer_invoice_list += `<td>` + (i+1) + `</td>
                <td>` + data[i]['invoice_id'] + `</td>
                <td>` + data[i]['date'] + `</td>
                <td>` + data[i]['payment_terms'] + `</td>
                <td class="right">` + number_formater(data[i]['invoice_amount']) + `</td>
                <td>` + data[i]['user_name'] + `</td>
                <td><a href="/invoice?view=invoice_manager&invoice_id=` + data[i]['invoice_id'] + `">View</a></td>
                <td><a href="/invoice?view=invoice_delete&invoice_id=` + data[i]['invoice_id'] + `">Delete</a></td></tr>`
            }
            customer_invoice_list += `<tr><td colspan="4" style="text-align:center;"><strong>Total Amount</strong></td><td>`+ total_amount +`</td></tr>`
            customer_invoice_list += `</table>`
            document.getElementById("customer_invoice_list").innerHTML = customer_invoice_list

        }else {
            document.getElementById("customer_invoice_list").innerHTML = no_data_template
        }
        hideLoader()
    } catch (error) {
        console.error('Error:', error);
        document.getElementById("customer_invoice_list").innerHTML = no_data_template
        hideLoader()
    }

}
async function customer_logs_load(customer_id) {
    showLoader()
    let no_data_template = `<br><br><hr>No Logs.`
    try {
        const response = await fetch(`/customer_logs_json/${customer_id}`);
        if (!response.ok) {
            document.getElementById("logs_table").innerHTML = no_data_template
            hideLoader()
        }
        let data = await response.json();
        if (data.length > 0){

            let log_table_code = `<br><br><hr><table>
            <tr><th colspan=6 style="text-align:center;">Logs</th></tr>
            <tr><th>Sr.</th><th>User ID</th><th>User Name</th><th>Date & Time</th><th>Type</th><th>Details</th></tr>
            `
            for (let i=0; i<data.length; i++){
                if (i+1 % 2 == 0){
                    log_table_code += `<tr class="dark">`
                } else {
                    log_table_code += `<tr class="light">`
                }
                log_table_code += `<td>`+ (i+1) +`</td>`
                log_table_code += `<td>`+ data[i]['user'] +`</td>`
                log_table_code += `<td>`+ data[i]['user_full_name'] +`</td>`
                log_table_code += `<td>`+ data[i]['date_time'] +`</td>`
                log_table_code += `<td>`+ data[i]['type'] +`</td>`
                log_table_code += `<td><pre>`+ data[i]['details'] +`</pre></td></tr>`
            }
            log_table_code += `</table>`

            document.getElementById("logs_table").innerHTML = log_table_code
            hideLoader()
        }else {
            document.getElementById("logs_table").innerHTML = no_data_template
        }
        hideLoader()
    } catch (error) {
        console.error('Error:', error);
        document.getElementById("logs_table").innerHTML = no_data_template
        hideLoader()
    }
}
async function add_customer(){
    showLoader()
    let no_data_template = `Error`
    try {
        const response = await fetch(`/salesman_details`);
        if (!response.ok) {
            document.getElementById("main_content").innerHTML = no_data_template
            hideLoader()
        }
        let data = await response.json();
        if (data){
            let add_customer_template = `
            <table>
                <tr><td>Customer Name</td><td><input type="text" id="customer_name" name="customer_name" required/></td></tr>
                <tr><td>Contact Number</td><td><input type="text" id="contact_number" name="contact_number" /></td></tr>
                <tr><td>Salesman Name</td><td id="addManual">
                    <select name="salesman_id" id="salesman_id" required>
                    <option value="" selected disabled hidden >Choose here</option>`

            for (let i=0; i<data.length;i++){
                add_customer_template += `<option value="` + data[i]['salesman_id'] + `">` + data[i]['salesman_name'] + `</option>`
            }
            add_customer_template += `</select><br>
                    <br>
                    <a href="/invoice?view=add_salesman">Add New Salesman</a>
                </td></tr>
            </table>
            <br>
            <button class="button" onClick="add_customer_submit()">Add Customer</button><br><br><div id="add_customer_message"></div>`
            document.getElementById("main_content").innerHTML = add_customer_template
        }else {
            document.getElementById("main_content").innerHTML = no_data_template
        }
        hideLoader()
    } catch (error) {
        console.error('Error:', error);
        document.getElementById("customer_invoice_list").innerHTML = no_data_template
        hideLoader()
    }
}
function todays_date(){
    // Get current date and time
var currentDate = new Date();

// Get year, month, and day
var year = currentDate.getFullYear();
var month = ('0' + (currentDate.getMonth() + 1)).slice(-2); // Months are zero-based
var day = ('0' + currentDate.getDate()).slice(-2);

// Format the date as "yyyy-mm-dd"
var formattedDate = year + '-' + month + '-' + day;
return formattedDate
}
async function add_customer_submit(){
    showLoader()
    let customer_name = document.getElementById('customer_name').value
    let contact_number = document.getElementById('contact_number').value
    let salesman_id = document.getElementById('salesman_id').value
    let error_template =`Some Error has occurred`
    try {
        const response = await fetch(`/add_customer?customer_name=${customer_name}&contact_number=${contact_number}&salesman_id=${salesman_id}`);
        if (!response.ok) {
            document.getElementById("add_customer_message").innerHTML = error_template
            hideLoader()
        }
        let data = await response.json();
        console.log(data)
        if (data == "Duplicate"){
            document.getElementById("add_customer_message").innerHTML = `This is a duplicate Customer.`
        }else {
            customer_data(data, 'invoice_id')
        }
        hideLoader()
    } catch (error) {
        console.error('Error:', error);
        document.getElementById("add_customer_message").innerHTML = error_template
        hideLoader()
    }
}
async function add_invoice(customer_id, customer_name){
    showLoader()
    let error_template = `Error Occurred`
    try {
        const response = await fetch(`/invoice_details?customer_id=${customer_id}&sort_by=desc&sort_string=invoice_id`);
        if (!response.ok) {
            document.getElementById("main_content").innerHTML = error_template
            hideLoader()
        }
        let data = await response.json();
        let add_invoice_template = `<table>
        <tr><td>Customer Name</td><td><input type="text" id="customer_name" name="customer_name" value="${customer_name}" readonly/></td></tr>
        <tr><td>Date</td><td><input type="date" id="date" name="date" value="` + todays_date() + `"/></td></tr>`
        if (data.length > 0){
            add_invoice_template += `<tr><td>Payment Terms (Optional)</td><td><input type="text" id="payment_terms" name="payment_terms" value="` + data[0]['payment_terms'] +`"/></td></tr>`
        } else {
            add_invoice_template += `<tr><td>Payment Terms (Optional)</td><td><input type="text" id="payment_terms" name="payment_terms" value=""/></td></tr>`
        }
        add_invoice_template += `<tr><td>Attention To (Optional)</td><td><input type="text" id="attention_to" name="attention_to" /></td></tr>
        <tr><td>Narration (Optional)</td><td><input type="text" id="narration" name="narration" /></td></tr>
        <tr><td>External Narration (Optional)</td><td><textarea id="narration_external" name="narration_external" rows="4" cols="50"></textarea></td></tr>
        </table>
        <br>
        <button class="button" onClick="add_invoice_submit(`+ customer_id +`)">Add Invoice</button>`
        hideLoader()
        document.getElementById("main_content").innerHTML = add_invoice_template
    } catch (error) {
        console.error('Error:', error);
        document.getElementById("main_content").innerHTML = error_template
        hideLoader()
    }
}
async function add_invoice_submit(customer_id){
    showLoader()
    let date = encodeURIComponent(document.getElementById('date').value)
    let payment_terms = encodeURIComponent(document.getElementById('payment_terms').value)
    let attention_to = encodeURIComponent(document.getElementById('attention_to').value)
    let narration = encodeURIComponent(document.getElementById('narration').value)
    let narration_external = encodeURIComponent(document.getElementById('narration_external').value)
    let error_template = `Error Occurred`
    console.log(customer_id)
    try {
        const response = await fetch(`/add_invoice?customer_id=${customer_id}&date=${date}&payment_terms=${payment_terms}&attention_to=${attention_to}&narration=${narration}&narration_external=${narration_external}`);
        if (!response.ok) {
            document.getElementById("main_content").innerHTML = error_template
            hideLoader()
        }
        let data = await response.json();
        if (data.length == 'Error'){
            document.getElementById("main_content").innerHTML = error_template
        } else {
            window.location.href = `/invoice?view=invoice_manager&invoice_id=${data}`;
        }
        hideLoader()

    } catch (error) {
        console.error('Error:', error);
        document.getElementById("main_content").innerHTML = error_template
        hideLoader()
    }
}
function number_formater(numberString){
    numberString = parseFloat(numberString);
    numberString = (numberString + 0.0000000001).toFixed(2);
    numberString = String(numberString)
    crossed_decimal = false;
    let output = ""
    for (i=0; i<numberString.length; i++){
        output = output + numberString[i];
        if (numberString[i] == "."){
            crossed_decimal = true;
        }
        if (crossed_decimal == false){
            let remaining_number = numberString.slice(i+1).split('.')[0];
            if (Number.isNaN(parseFloat(remaining_number)) == false){
                if (remaining_number.length % 3 == 0){
                    output = output + ","
                }
            }
        }
    }
    return output;
}
function logs(){
    if (sessionStorage.getItem("log_show") == "true"){
        sessionStorage.removeItem("log_show")
        document.getElementById("log_button").textContent = "Show Logs"
        document.getElementById("logs_table").style.display = 'none'
    } else {
        sessionStorage.setItem("log_show", "true")
        document.getElementById("log_button").textContent = "Hide Logs"
        document.getElementById("logs_table").style.display = ''
    }
}
if (window.location.hash.length > 0){
    let customer_id_url = parseInt(window.location.hash.replace("#",''))
    customer_data(customer_id_url,'invoice_id');

    removeFragment();
}
    else {
        load_customer_list('customer_name');
}
