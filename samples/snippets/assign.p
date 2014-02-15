program AssignTest;
const
   OK  = 'OK';
   ERR = 'ERROR';
var
   r	: real;
   i, j	: integer;
   b	: boolean;
   a1	: array[0..10] of char;
   a2	: array[0..10] of char;
begin
   r := 3.14;
   i := 2;
   j := i;
   b := true;

   if b then
      writeln(OK)
   else
      writeln(ERR);
   
   a1 := ERR;
   a2 := OK;
   writeln(a2[0], a2[1]);
   a1 := a2;
   if j = 2 then
      writeln(OK)
   else
      halt(1);

   i := 5;

   if i = 5 then
      writeln(OK)
   else
      halt(1);

   j := 3;

   if j = 3 then
      writeln(OK)
   else
      halt(1);
   
   writeln(a1[0], a1[1]);
end.

