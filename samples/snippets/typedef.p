program TypeDefTest;
const
   OK	     = 'OK';
   ERR	     = 'ERROR';
   MAX_DIGIT = 9;
   MIN_DIGIT = 0;

type
   T_BOOL  = boolean;
   T_DIGIT = MIN_DIGIT..MAX_DIGIT; 
   T_INT8  = 0..255;
var
   i : T_DIGIT;
   r : real;
   j : T_INT8;
begin
   r := 3.14;
   i := 2;
   j := i;
   writeln(OK);
end.

