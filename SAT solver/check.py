import sys
import os


if __name__ == "__main__":
    model_file = sys.argv[1]
    model_fp = open(model_file, "r")
    if(model_fp.readline()=="SAT\n"):
        model = [k for k in model_fp.readline().split()]

    check_file = sys.argv[2]
    check_fp = open(check_file, "r")
    detail_line = check_fp.readline()
    num_clauses = int(detail_line.split()[3])
    for i in range (num_clauses):
        c = check_fp.readline().split()
        for j in c:
            if j in model:
                flag=True
                break
            flag=False
        if(flag==False):
            print(c)
