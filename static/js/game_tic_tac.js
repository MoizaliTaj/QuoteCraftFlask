let X = "X"
let O = "O"
let last_move = null;
let rows = [["00", "01", "02"], ["10", "11", "12"], ["20", "21", "22"],]
let cols = [["00","10","20"], ["01","11","21"], ["02","12","22"]]
let diagonal = [["00","11","22"], ["20","11","02"]]
let master = [rows, cols, diagonal]
let human_player = null

function make_a_move(i,j,node){
    document.getElementById(String(i) + String(j)).innerHTML = node;
    last_move = node;
    if (check_for_win(node,current_state_to_board()) == true){
        document.getElementById("message").innerHTML = check_for_win_master()
        disable_board()
    } else if (check_for_win(X,current_state_to_board()) == "Draw"){
        document.getElementById("message").innerHTML = "Game ended in a Draw"
        disable_board()
    } else {
        auto_move()
    }
}
function make_a_move_master(i,j){
    if (((last_move == null) || (last_move == O)) && (document.getElementById(String(i) + String(j)).innerHTML == "")){
        make_a_move(i,j,X)
    } else if((last_move == X)  && (document.getElementById(String(i) + String(j)).innerHTML == "")) {
        make_a_move(i,j,O)
    }
}

function check_for_win(node, board){
    let won = false;
    master.forEach(function(sub_element) {
        sub_element.forEach(function(element) {
            let node_count = 0;
            element.forEach(function(coordinates) {
                if (board[parseInt(coordinates[0])][parseInt(coordinates[1])] == node){
                    node_count += 1
                }
            });
            if (node_count == 3){
                won = true;
            }
        });
    });
    let null_count = 0
    master.forEach(function(sub_element) {
        sub_element.forEach(function(element) {
            let node_count = 0;
            element.forEach(function(coordinates) {
                if (board[parseInt(coordinates[0])][parseInt(coordinates[1])] == ""){
                    null_count += 1
                }
            });
        });
    });
    if (null_count == 0){
        return "Draw"
    }
    return won;
}
function disable_board(){
    let won = false;

    master.forEach(function(sub_element) {
        sub_element.forEach(function(element) {
            let node_count = 0;
            element.forEach(function(coordinates) {
                document.getElementById(coordinates).removeAttribute("onclick");
            });
        });
    });
}
function check_for_blocking_coordinates(board, node){
    master_block_coordinate = []
    master.forEach(function(sub_element) {
        sub_element.forEach(function(element) {
            let node_count = 0;
            let null_count = 0;
            let potential_block_coordinate = null
            element.forEach(function(coordinates) {
                if (board[parseInt(coordinates[0])][parseInt(coordinates[1])] == ""){
                    null_count += 1
                    potential_block_coordinate = coordinates
                } else if (board[parseInt(coordinates[0])][parseInt(coordinates[1])] == node){
                    node_count += 1
                }
            });
            if ((node_count == 2) && (null_count ==1)){
                master_block_coordinate.push(potential_block_coordinate)
            }
        });
    });
    return master_block_coordinate
}

function check_for_pottential_win_lines(board, node){
    let potential_win_lines = 0
    master.forEach(function(sub_element) {
        sub_element.forEach(function(element) {
            let node_count = 0;
            let null_count = 0;
            element.forEach(function(coordinates) {
                if (board[parseInt(coordinates[0])][parseInt(coordinates[1])] == ""){
                    null_count += 1
                } else if (board[parseInt(coordinates[0])][parseInt(coordinates[1])] == node){
                    node_count += 1
                }
            });
            if ((node_count == 2) && (null_count ==1)){
                potential_win_lines += 1
            }
        });
    });
    return potential_win_lines;
}
function max_future_lines(node, board){
    let max_future_lines = 0;
    master.forEach(function(sub_element) {
        sub_element.forEach(function(element) {
            let node_count = 0;
            element.forEach(function(coordinates) {
                if ((board[parseInt(coordinates[0])][parseInt(coordinates[1])] == "") || (board[parseInt(coordinates[0])][parseInt(coordinates[1])] == node)){
                    node_count += 1
                }
            });
            if (node_count == 3){
                max_future_lines += 1
            }
        });
    });
    return max_future_lines
}
function current_state_to_board(){
    let rows = [["00", "01", "02"], ["10", "11", "12"], ["20", "21", "22"],]
    let final_board = []
    rows.forEach(function(row) {
        let row_data = []
        row.forEach(function(cordinate) {
            row_data.push(document.getElementById(cordinate).innerHTML)
        });
        final_board.push(row_data)
    });
    return final_board
}
function eval_master(current_board, proposed_move, node){

    // basic check how many line are possible by each player and difference between the same
    final_score = max_future_lines(X, proposed_move) - max_future_lines(O, proposed_move)

    // check if a given player has won the game then provide maximum score as that is the ultimate goal
    if (check_for_win(node, proposed_move) == true){
        if (node == X){
            return 100
        } else {
            return -100
        }
    }

    // block other players win move
    if (last_move == X){
        // check if x is going to win in next round if a position is not blocked
        blocking_cordinates = check_for_blocking_coordinates(current_board, X)
        if (blocking_cordinates.length > 0){
            // check if porposed move will block this cordinates
            blocking_cordinates.forEach(function(cordinate) {
                if (proposed_move[parseInt(cordinate[0])][parseInt(cordinate[1])] == O){
                    final_score -= 50
                }
            });
        } else{
            if (check_for_pottential_win_lines(current_board,O) > 0){
                final_score -= ((check_for_pottential_win_lines(current_board,O) * 3) + 15)
            } else {
                final_score += ((check_for_pottential_win_lines(current_board,X) * 3) + 0)
            }
        }
    }

    if (last_move == O){
        // check if O is going to win in next round if a position is not blocked
        blocking_cordinates = check_for_blocking_coordinates(current_board, O)
        if (blocking_cordinates.length > 0){
            // check if porposed move will block this cordinates
            blocking_cordinates.forEach(function(cordinate) {
                if (proposed_move[parseInt(cordinate[0])][parseInt(cordinate[1])] == X){
                    final_score += 50
                }
            });
        } else{
            if (check_for_pottential_win_lines(current_board,X) > 0){
                final_score += ((check_for_pottential_win_lines(current_board,X) * 3) + 15)
            }
            else{
                final_score -= ((check_for_pottential_win_lines(current_board,O) * 3) + 0)
            }
        }
    }
    return final_score
}

function board_copier(board_){
    let new_board = [["","",""],["","",""],["","",""],]
    for (let i=0; i<3 ; i++){
        for (let j=0; j<3 ; j++){
            if (board_[i][j] != ""){
                new_board[i][j] = board_[i][j]
            }
        }
    }
    return new_board
}
function random_number(lower_bound, upper_bound){
    return (Math.floor(Math.random() * (upper_bound+1))) + lower_bound;
}
function make_move(current_board, proposed_move){
    for (let i=0; i<3 ; i++){
        for (let j=0; j<3 ; j++){
            if (current_board[i][j] != proposed_move[i][j]){
                if (proposed_move[i][j] == X){
                    make_a_move(i,j,X)
                } else if (proposed_move[i][j] == O){
                    make_a_move(i,j,O)
                }
            }
        }
    }
}

function move_gen(board_, for_node){
    let infinity = Math.pow(10, 1000);
    let empty_coordinates = []
    let next_moves = []
    for (let i=0; i<3 ; i++){
        for (let j=0; j<3 ; j++){
            if (board_[i][j] == ""){
            empty_coordinates.push(String(i) + String(j))
            }
        }
    }
    empty_coordinates.forEach(function(coordinates) {
        let proposed_move = board_copier(board_)
        proposed_move[parseInt(coordinates[0])][parseInt(coordinates[1])] = for_node
        next_moves.push([board_copier(board_), proposed_move])
    });
    let max_score = -infinity
    let min_score = infinity
    let best_moves = []
    if (for_node == X){
        next_moves.forEach(function(data) {
            let current_position = data[0]
            let proposed_move = data[1]
            if (eval_master(current_position, proposed_move, for_node) > max_score){
                max_score = eval_master(current_position, proposed_move, for_node)
                best_moves = [proposed_move]
            } else if (eval_master(current_position, proposed_move, for_node) == max_score){
                best_moves.push(proposed_move)
            }
        });
    } else if (for_node == O){
        next_moves.forEach(function(data) {
            let current_position = data[0]
            let proposed_move = data[1]
            if (eval_master(current_position, proposed_move, for_node) < min_score){
                min_score = eval_master(current_position, proposed_move, for_node)
                best_moves = [proposed_move]
            } else if (eval_master(current_position, proposed_move, for_node) == min_score){
                best_moves.push(proposed_move)
            }
        });
    }
    if (best_moves.length > 0){
        return best_moves[random_number(0,best_moves.length-1)]
    } else {
        return []
    }
}

function check_for_win_master(){
    let current_board = current_state_to_board()
    if (check_for_win(X, current_board)){
        if (human_player == X){
            return "You won the Game."
        } else{
            return "Computer won the Game."
        }
    } else if (check_for_win(O, current_board)){
        if (human_player == O){
            return "You won the Game."
        } else{
            return "Computer won the Game."
        }
    } else {
        for (let i=0; i<3 ; i++){
            for (let j=0; j<3 ; j++){
                if (current_board[i][j] == ""){
                    return ""
                }
            }
        }
        return "Game ended in a draw."
    }

}
function auto_move(){
    let current_board = current_state_to_board()
    if ((human_player == X) && (check_for_win_master() != "Game ended in a draw.")){
        if ((last_move != null) && (last_move != O)){
            make_move(current_board,move_gen(current_board, O))
        }
    } else if ((human_player == O) && (check_for_win_master() != "Game ended in a draw.")){
        if ((last_move == null) || (last_move == O)){
            make_move(current_board,move_gen(current_board, X))
        }
    }
}
function reset_game(){
    human_player = null;
    last_move = null;
    document.getElementById("message").innerHTML = "";
    setup_game();

}
let template = `
<table>
    <tr>
        <td id="00" onclick="make_a_move_master(0,0)"></td>
        <td id="01" onclick="make_a_move_master(0,1)"></td>
        <td id="02" onclick="make_a_move_master(0,2)"></td>
    </tr><tr>
        <td id="10" onclick="make_a_move_master(1,0)"></td>
        <td id="11" onclick="make_a_move_master(1,1)"></td>
        <td id="12" onclick="make_a_move_master(1,2)"></td>
    </tr><tr>
        <td id="20" onclick="make_a_move_master(2,0)"></td>
        <td id="21" onclick="make_a_move_master(2,1)"></td>
        <td id="22" onclick="make_a_move_master(2,2)"></td>
    </tr>
</table><br>
    <button onclick=reset_game()>Reset this game</button>
`
function humman_player_setup(name){
    if (name == "X"){
        human_player = X
        document.getElementById("game").innerHTML = template
        auto_move()
    } else if (name == "O"){
        human_player = O
        document.getElementById("game").innerHTML = template
        auto_move()
    } else {
        setup_game
    }

}

function setup_game(){
    document.getElementById("game").innerHTML = "<h2>Choose Player</h2><button onclick=humman_player_setup('X')>Player X</button>&nbsp;&nbsp;&nbsp;<button onclick=humman_player_setup('O')>Player O</button>"
}
if (human_player == null){
    setup_game()
}