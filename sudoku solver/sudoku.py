import sys
import os
import numpy as np
import time
import random

def solve_sudoku(inputSudokuFile, choice = 1):
    """
    Solves an incomplete grid.
    Args:
        inputSudokuFile: File pointer to the input sudoku incomplete grid
        choice: Flag to see where we need to solve or generate
    """
    generate_complete_input(inputSudokuFile, choice)
    exec_cmd = '/bin/minisat cnf_propositions.txt output.txt > /dev/null'
    exit_status = os.system(exec_cmd)
    try:
        result_fp = open('output.txt', 'r')
        if(result_fp.readline()=='SAT\n'):
            if(choice==1):
                print_sudoku(result_fp)
        else:
            if(choice ==1):
                print("Sudoku is not solveable.")
            else:
                return 0
        result_fp.close()
    except IOError:
        print('Minisat could not run, please check if installation is correct.')
        exit()

def print_sudoku(result_fp, parsed_output_file='parsed_output.txt', choice = 1):
    """
    Print out the resultant sudoku from minisat output format and write
    to parsed_output_file
    Args:
        result_fp: File pointer to the Minisat output.
                   This is not the final parsed output.
        parsed_output_file: This is the file where the final
        output is written from the minisat output
        choice: Flag to see where we need to solve or generate
    """
    parsed_fp = open(parsed_output_file, 'w+')
    res = result_fp.readline().split()
    for i in range (9):
        for j in range (9):
            for k in range (9):
                if(int(res[81*i+9*j+k])>0):
                    parsed_fp.write("{} ".format(int(res[81*i+9*j+k])-81*i-9*j))
                    break
        parsed_fp.write("\n")
    parsed_fp.close()
    if(choice==1):
        print_cmd = 'cat {}'.format(parsed_output_file)
        os.system(print_cmd)

def generate_complete_input(input_sudoku_file, choice=1):
    """
    Generates the complete list of clauses and writes to
    cnf_propositions.txt
    Args:
        input_sudoku_file: File pointer to the original incomplete grid
        choice: Flag to use existing utility function with additional features
        required to make a new puzzle:
            default=1 when nothing different is done

    """
    grid_propositions = np.arange(1,730)
    grid_propositions = grid_propositions.reshape(9,9,9)
    input_file = open("cnf_propositions.txt", "w+")
    extra_clauses = count_input(input_sudoku_file, choice)
    input_file.write("p cnf 729 {}\n".format((3258+extra_clauses)))

    #The clauses can be played around with as required

    atleast_one_number_in_each_entry(grid_propositions, input_file)
    atmost_one_number_in_each_entry(grid_propositions, input_file)
    atleast_each_number_in_row(grid_propositions, input_file)
    #unique_number_in_row(grid_propositions, input_file)
    atleast_each_number_in_col(grid_propositions, input_file)
    #unique_number_in_col(grid_propositions, input_file)
    atleast_each_number_in_subgrid(grid_propositions, input_file)
    #unique_number_in_subgrid(grid_propositions, input_file)
    atleast_each_number_in_diagonals(grid_propositions, input_file)
    #unique_number_in_diagonals(grid_propositions, input_file)
    parse_input_sudoku_file(grid_propositions, input_file, input_sudoku_file, choice)
    input_file.close()
    input_sudoku_file.close()

def count_input(sudoku_fp, choice = 1):
    """
    To count the number of extra clauses required
    """
    T = sudoku_fp.read()
    R = [i.split() for i in T.split('\n')]
    count = 0
    for i in range (9):
        for j in range (9):
            if(R[i][j]!='.'):
                count+=1

    sudoku_fp.seek(0)
    if(choice!=1):
        count+=1
    return count

def parse_input_sudoku_file(propositions, input_fp, sudoku_fp, choice=1):
    """
    Parse the input file in the . format to generate all extra clauses
    Args:
        propositions: Array of numbers
        input_fp: File pointer for the input to MiniSAT
        sudoku_fp: File pointer for the input grid

    """
    #todo: Check for incorect inputs
    T = sudoku_fp.read()
    R = [i.split() for i in T.split('\n')]

    for i in range (9):
        for j in range (9):
            if(R[i][j]!='.'):
                input_fp.write("{} 0\n".format(propositions[i][j][int(R[i][j])-1]))

    if(choice!=1):
        answer_fp = open('answer.txt', 'r')
        T1 = answer_fp.read()
        R1 = [i.split() for i in T1.split('\n')]

        for i in range (9):
            for j in range(9):
                if(R[i][j]=='.'):
                    input_fp.write("-{} ".format(propositions[i][j][int(R1[i][j])-1]))
        input_fp.write("0\n")
        answer_fp.close()


def atleast_one_number_in_each_entry(propositions, fp):
    """
      Auxillary function to list out clauses
      to maintain each entry has atleast one number
      and write to file.
    """
    for i in range (9):
        for j in range (9):
            for k in range (9):
                fp.write("{} ".format(propositions[i][j][k]))
            fp.write("0\n")


def atmost_one_number_in_each_entry(propositions, fp):
    """
    Auxillary function to list out clauses
    to maintain each entry has atmost one number
    and write to file.
    """
    for i in range (9):
        for j in range (9):
            for k1 in range (9):
                for k2 in range (k1+1,9):
                    fp.write("-{} -{} 0\n".format(propositions[i][j][k1],propositions[i][j][k2]))


def atleast_each_number_in_row(propositions, fp):
    """
    Auxillary function to list out clauses
    to maintain each number appears atleast once in
    each row and write to file.
    """
    for i in range (9):
        for k in range (9):
            for j in range (9):
                fp.write("{} ".format(propositions[i][j][k]))
            fp.write("0\n")

def unique_number_in_row(propositions, fp):
    """
      Auxillary function to list out clauses
      to maintain each row has unique numbers
      and write to file.

    """
    for j in range (9):
        for k in range (9):
            for i in range (8):
                for x in range (i+1,9):
                    fp.write("-{} -{} 0\n".format(propositions[x][j][k], propositions[i][j][k]))

def atleast_each_number_in_col(propositions, fp):
    """
    Auxillary function to list out clauses
    to maintain each number appears atleast once in
    each column and write to file.
    """
    for j in range (9):
        for k in range (9):
            for i in range (9):
                fp.write("{} ".format(propositions[i][j][k]))
            fp.write("0\n")

def unique_number_in_col(propositions, fp):
    """
      Auxillary function to list out clauses
      to maintain each column has unique numbers
      and write to file.

    """
    for i in range (9):
        for k in range (9):
            for j in range (8):
                for y in range (i+1,9):
                    fp.write("-{} -{} 0\n".format(propositions[i][j][k], propositions[i][y][k]))

def atleast_each_number_in_subgrid(propositions, fp):
    """
    Auxillary function to list out clauses
    to maintain each number appears atleast once in
    each subgrid and write to file.
    """
    for x in range (3):
        for y in range (3):
            for k in range (9):
                for i in range (3):
                    for j in range (3):
                        fp.write("{} ".format(propositions[3*x+i][3*y+j][k]))
                fp.write("0\n")

def unique_number_in_subgrid(propositions, fp):
    """
      Auxillary function to list out clauses
      to maintain each subgrid has unique numbers
      and write to file.

    """
    for k in range (9):
        for x in range (3):
            for y in range (3):
                for i in range (3):
                    for j in range (3):
                        for z in range (j+1,3):
                            fp.write("-{} -{} 0\n".format(propositions[3*x+i][3*y+j][k], propositions[3*x+i][3*y+z][k]))

    for k in range (9):
        for x in range (3):
            for y in range (3):
                for i in range (3):
                    for j in range (3):
                        for z in range (i+1,3):
                            for l in range (3):
                                fp.write("-{} -{} 0\n".format(propositions[3*x+i][3*y+j][k], propositions[3*x+z][3*y+l][k]))

def atleast_each_number_in_diagonals(propositions, fp):
    """
    Auxillary function to list out clauses
    to maintain each number appears atleast once in
    each diagonals and write to file.
    """
    for k in range (9):
        for i in range (9):
            fp.write("{} ".format(propositions[i][i][k]))
        fp.write("0\n")

    for k in range (9):
        for i in range (9):
            fp.write("{} ".format(propositions[i][8-i][k]))
        fp.write("0\n")


def unique_number_in_diagonals(propositions, fp):
    """
      Auxillary function to list out clauses
      to maintain each diagonal has unique numbers
      and write to file.

    """
    for i in range (8):
        for k in range (9):
            for j in range (i+1,9):
                fp.write("-{} -{} 0\n".format(propositions[i][i][k], propositions[j][j][k]))

    for i in range (8):
        for k in range (9):
            for j in range (i+1,9):
                fp.write("-{} -{} 0\n".format(propositions[i][8-i][k], propositions[j][8-j][k]))

def generate_sudoku(puzzle_file_name, choice=2):
    """
    Generates a random sudoku using -rnd-init
    setting the Linux time stamp as seed to minisat
    Args:
        puzzle_file_name: File name where the user wants an incomplete grid
    """
    #Prepare the cnf_propositions file for the final answer
    try:
        with open('empty_doku.txt', 'r') as f:
            generate_complete_input(f)
    except IOError:
        print("The empty sudoku file was not found. Please provide one in the correct format")

    #Generate a complete random grid at answer.txt
    lts = time.time()
    exec_cmd = '/bin/minisat -rnd-init -rnd-seed={} cnf_propositions.txt output.txt > /dev/null'.format(lts)
    exit_status = os.system(exec_cmd)
    with open('output.txt', 'r') as f:
        f.readline()
        print_sudoku(f, 'answer.txt', 2)

    if(choice=='3'):
        print("Here's some random fun - ")
        with open('answer.txt', 'r') as final:
            L = [i.split() for i in final.read().split('\n')]
            for i in range (9):
                for j in range (8):
                    print("{} ".format(L[i][j]), end='', flush=True)
                print("{}\n".format(L[i][8]), end='', flush=True)
        exit()


    # Start to pop elements
    fp = open('answer.txt', 'r')
    T = fp.read()
    # R is a list of lists for the complete sudoku at any point
    R = [i.split() for i in T.split('\n')]
    status_map = [i for i in range (0,81)]
    while(status_map!=[]):
        rand_pos = random.SystemRandom().choice(status_map)
        status_map.remove(rand_pos)
        puzzle_fp = open(puzzle_file_name, 'w+')

        #Prepare the puzzle file with incomplete grid for verification
        for i in range (9):
            for j in range (8):
                if(i is not int(rand_pos/9) or j is not (rand_pos%9)):
                    puzzle_fp.write("{} ".format(R[i][j]))
                else:
                    puzzle_fp.write(". ")
            if(i==int(rand_pos/9) & (rand_pos%9)==8):
                puzzle_fp.write(".\n")
            else:
                puzzle_fp.write("{}\n".format(R[i][8]))
        puzzle_fp.flush()
        puzzle_fp.seek(0)

        #Check if the solution is unique
        return_status = solve_sudoku(puzzle_fp, 2)
        if(return_status==0):
            R[int(rand_pos/9)][rand_pos%9]='.'
        else:
            continue

    print("Here you go. Happy Sudoku Hours. :)")
    with open(puzzle_file_name, 'r') as final:
        L = [i.split() for i in final.read().split('\n')]
        for i in range (9):
            for j in range (8):
                print("{} ".format(L[i][j]), end='', flush=True)
            print("{}\n".format(L[i][8]), end='', flush=True)

    print("You can always look at the answer at answer.txt")

if __name__ == '__main__':
    choice = input("Enter 1 to put your sudoku worries to rest, anything else to bring them sudoku worries back.\nEnter 3 to get a completely random sudoku. ")
    if(choice == '1'):
        inputFileName = input("Enter the filename of the input sudoku. The default name is input.txt ")
        if(inputFileName == ''):
            try:
                solve_sudoku(open('input.txt', "r"))
            except IOError:
                print("Could not read from input.txt")
        else:
            try:
                solve_sudoku(open(inputFileName, "r"))
            except IOError:
                print("Could not read file {}".format(inputFileName))
    else:
        if(choice!='3'):
            puzzleName = input("Enter what you want to call your puzzle. Default is puzzle.txt and you can find the solution at answer.txt ")
            if(puzzleName == ''):
                generate_sudoku('puzzle.txt', choice)
            else:
                generate_sudoku(puzzleName, choice)
        else:
            generate_sudoku('random.txt', choice)

