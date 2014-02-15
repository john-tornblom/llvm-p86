#!/bin/bash

argc=$#
red="\e[0;31m"
green="\e[0;32m"
nc="\e[0m"

function run_test_case {
    ./llvm-p86 -e "samples/snippets/$1" > /dev/null 2>&1
    status=$?
    str=$(printf "%-30s %s" $1)
    if [ $status -ne 0 ]; then
	echo -e "${str} ${red}FAIL${nc}"
    else
	echo -e "${str} ${green}PASS${nc}"
    fi
}

function test {
    # spawn if argc is anything but one
    if [ $argc -ne 1 ]; then
        run_test_case $1
    else
        run_test_case $1 &
    fi
}

echo ""
echo ""
echo "Running snippets from $(pwd)/samples/snippets/"
echo ""

test "array.p"
test "assign.p"
test "assign2.p"
test "builtins.p"
test "case.p"
test "cast.p"
test "comparisons.p"
test "const.p"
test "enum.p"
test "folding.p"
test "function.p"
test "if.p"
test "if_else.p"
test "include.p"
test "int_calc.p"
test "label.p"
test "linked_list.p"
test "logic.p"
test "loop_for.p"
test "loop_repeat.p"
test "loop_while.p"
test "nested_function1.p"
test "nested_function2.p"
test "nested_function3.p"
test "nested_proc.p"
test "opttest.p"
test "params.p"
test "parsetest3.p"
test "pointer.p"
test "procedure.p"
test "procedure1.p"
test "real_calc1.p"
test "real_calc2.p"
test "real_calc3.p"
test "real_calc4.p"
test "record.p"
test "record2.p"
test "scopes.p"
test "semtest.p"
test "sets.p"
test "signes.p"
test "simple.p"
test "simple_array.p"
test "simple_case.p"
test "simple_function.p"
test "simple_record.p"
test "typedef.p"
test "types.p"
test "unnamed_record.p"
test "variant.p"
test "with.p"

wait
