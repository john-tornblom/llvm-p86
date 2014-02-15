program SimpleFunctionTest;

var
   i : integer;
   
function onearg(arg: integer) : integer;
begin
   onearg := arg;
end; { onearg }

begin   
   if onearg(5) = 5 then
      writeln("OK")
   else
      halt(1);

   i := 0;
   if onearg(i) = 0 then
      writeln("OK")
   else
      halt(1);
end.