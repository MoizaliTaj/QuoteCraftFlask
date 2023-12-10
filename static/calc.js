function CalcToggle(){
let calccode =`
                    <button class="button" onclick="CalcToggle()">Calculator</button>
                    <table class="calctable" >
                        <tr class="calctr">
                            <td class="calctd" colspan="4"><input value="" id="calc-out" placeholder="Output" readonly></td>
                        </tr>
                        <tr class="calctr">
                            <td class="calctd"><button class="button-calc" id="7" onclick="add_calc('7')">7</button></td>
                            <td class="calctd"><button class="button-calc" id="8" onclick="add_calc('8')">8</button></td>
                            <td class="calctd"><button class="button-calc" id="9" onclick="add_calc('9')">9</button></td>
                            <td class="calctd"><button class="button-calc" id="x" onclick="add_calc('*')">X</button></td>
                        </tr><tr class="calctr">
                            <td class="calctd"><button class="button-calc" id="4" onclick="add_calc('4')">4</button></td>
                            <td class="calctd"><button class="button-calc" id="5" onclick="add_calc('5')">5</button></td>
                            <td class="calctd"><button class="button-calc" id="6" onclick="add_calc('6')">6</button></td>
                            <td class="calctd"><button class="button-calc" id="/" onclick="add_calc('/')">/</button></td>
                        </tr><tr class="calctr">
                            <td class="calctd"><button class="button-calc" id="1" onclick="add_calc('1')">1</button></td>
                            <td class="calctd"><button class="button-calc" id="2" onclick="add_calc('2')">2</button></td>
                            <td class="calctd"><button class="button-calc" id="3" onclick="add_calc('3')">3</button></td>
                            <td class="calctd"><button class="button-calc" id="-" onclick="add_calc('-')">-</button></td>
                        </tr><tr class="calctr">
                            <td class="calctd"><button class="button-calc" id="." onclick="add_calc('.')">.</button></td>
                            <td class="calctd"><button class="button-calc" id="0" onclick="add_calc('0')">0</button></td>
                            <td class="calctd"><button class="button-calc" id="=" onclick="cal_calc()">=</button></td>
                            <td class="calctd"><button class="button-calc" id="+" onclick="add_calc('+')">+</button></td>
                        </tr><tr class="calctr">
                            <td class="calctd" colspan="2"><button class="button-calc" id="clear" onclick="cleanit()">Clear</button></td>
                            <td class="calctd" colspan="2"><button class="button-calc" id="back" onclick="backSpace()">&nbsp;&nbsp;⌫&nbsp;&nbsp;</button></td>
                        </tr>
                    </table>
`
var MyDiv = document.getElementById('DIV1').innerHTML.length;
    if (MyDiv < 100){
        document.getElementById('DIV1').innerHTML = calccode;
    }
    else {
        document.getElementById('DIV1').innerHTML = `<button class="button" onclick="CalcToggle()">Calculator</button>`;
    }
}
function add_calc(input_str){
    let current_val = document.getElementById("calc-out").value;
    document.getElementById("calc-out").value = current_val + input_str;
}
function add_calc_operators(input_str){
    let current_val = document.getElementById("calc-out").value;
    if (current_val.slice(-1) === "/" || current_val.slice(-1) === "*" || current_val.slice(-1) === "-" || current_val.slice(-1) === "+"){
        current_val = current_val.substr(0,current_val.length-1)
    }
    document.getElementById("calc-out").value = current_val + input_str;
}
function cal_calc(){
    let calculation_str = document.getElementById("calc-out").value;
    document.getElementById("calc-out").value = eval(calculation_str);
}
function cleanit(){
    document.getElementById("calc-out").value = '';
}
function backSpace(){
    let current_val = document.getElementById("calc-out").value;
    document.getElementById("calc-out").value = current_val.substr(0,current_val.length-1)
}
function animate(ID){
        document.getElementById(ID).style.backgroundColor = "#2c974b";
        setTimeout(function() {
            document.getElementById(ID).style.backgroundColor = "white"
        }, 200);
}

document.addEventListener('keyup', (e) => {
    if (e.code === "Numpad7" || e.code === "Digit7"){
        add_calc('7');
        animate("7");
    }
    else if (e.code === "Numpad8" || e.code === "Digit8"){
        add_calc('8');
        animate("8");
    }
    else if (e.code === "Numpad9" || e.code === "Digit9"){
        add_calc('9');
        animate("9");
    }
    else if (e.code === "Numpad4" || e.code === "Digit4"){
        add_calc('4');
        animate("4");
    }
    else if (e.code === "Numpad5" || e.code === "Digit5"){
        add_calc('5');
        animate("5");
    }
    else if (e.code === "Numpad6" || e.code === "Digit6"){
        add_calc('6');
        animate("6");
    }
    else if (e.code === "Numpad1" || e.code === "Digit1"){
        add_calc('1');
        animate("1");
    }
    else if (e.code === "Numpad2" || e.code === "Digit2"){
        add_calc('2');
        animate("2");
    }
    else if (e.code === "Numpad3" || e.code === "Digit3"){
        add_calc('3');
        animate("3");
    }
    else if (e.code === "Numpad0" || e.code === "Digit0"){
        add_calc('0');
        animate("0");
    }
    else if (e.code === "NumpadDecimal" || e.code === "Period"){
        add_calc('.');
        animate(".");
    }
    else if (e.code === "NumpadEnter" || e.code === "Enter"){
        cal_calc();
        animate("=");
    }
    else if (e.code === "NumpadDivide"){
        add_calc_operators('/');
        animate("/");
    }
    else if (e.code === "NumpadMultiply"){
        add_calc_operators('*');
        animate("x");
    }
    else if (e.code === "NumpadSubtract"){
        add_calc_operators('-');
        animate("-");
    }
    else if (e.code === "NumpadAdd"){
        add_calc_operators('+');
        animate("+");
    }
    else if (e.code === "Escape"){
        cleanit();
        animate("clear");
    }
    else if (e.code === "Backspace"){
        backSpace();
        animate("back");
    }

});
