let keysPressed = {}

document.addEventListener('keydown', (event) => {
   keysPressed[event.key] = true;
   if (keysPressed['Alt'] && ( event.key == 'p' ||  event.key == 'P')) {
      keysPressed = {}
      try {
         document.getElementById("normal_print").submit();
      }
      catch {}
   }
   else if (keysPressed['Alt'] && ( event.key == 'o' ||  event.key == 'O')) {
      keysPressed = {}
      try {
         document.getElementById("odd_print").submit();      
      }
      catch {}
   }
   else if (keysPressed['Alt'] && ( event.key == 'c' ||  event.key == 'C')) {
      keysPressed = {}
      CalcToggle()
   }
   else if (keysPressed['Alt'] && ( event.key == 'u' ||  event.key == 'U')) {
      keysPressed = {};
      try {
      console.log(document.getElementById("update_form").submit());
      }
      catch {}
   }
});

document.addEventListener('keyup', (event) => {
   keysPressed = {}
});

