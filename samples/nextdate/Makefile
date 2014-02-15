P86C    ?= ../../llvm-p86
CC      ?= gcc

OPERATOR ?= dcc
P_FLAGS  ?= -O0 -I./src
M_FLAGS  ?= -r../../wwwroot/data -m$(OPERATOR)
LD_FLAGS ?= -lm

SOURCES := $(wildcard src/*.p86)
TESTS   := $(wildcard test/*.p86)

OBJECTS := $(addprefix obj/, $(notdir $(TESTS:.p86=.o)))
MUTANTS := $(addprefix obj/, $(notdir $(SOURCES:.p86=.mut)))

EXECUTABLE := nextdate

all: $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS) $(MUTANTS)
	$(CC) $(OBJECTS) $(MUTANTS) $(LD_FLAGS) -o $@


obj/%.mut: src/%.p86
	$(P86C) $(P_FLAGS) $(M_FLAGS) -o $@ $<


obj/%.o: test/%.p86
	$(P86C) $(P_FLAGS) -o $@ $<

clean:
	rm -rf *~
	rm -rf obj
	rm -rf $(EXECUTABLE)

