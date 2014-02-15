program ProcedureTest;
var
   i : integer;
   r : real;

procedure isum(num1 : integer; num2 : integer);
begin
   i := num1 + num2;
end; { isum }

procedure msum(num1: integer; num2 : real);
begin
   r := num1 + num2;
end; { msum }

procedure fsum(num: real; num2 : real);
begin
   r := num + num2;
end; { fsum }

procedure onearg(arg : integer);
begin
   i := arg;
end; { onearg }

BEGIN
   i := 1;
   r := 0;
   
   isum(1, 2);
   if i = 3 then
      writeln("OK")
   else
      halt(1);

   msum(2, 2);
   if r = 4 then
      writeln("OK")
   else
      halt(1);

   fsum(5, 2);
   if r = 7 then
      writeln("OK")
   else
      halt(1);

   onearg(5);
   if i = 5 then
      writeln("OK")
   else
      halt(1);
end.