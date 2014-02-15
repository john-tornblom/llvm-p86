program FunctionTest;
const
   PI =  3.14;
   
var 
   i : integer;
   r : real;
     
function isum(num1 : integer; num2 : integer) : integer;
begin
   isum := num1 + num2;
   num1 := 0;
end; { isum }

function msum(num1 : integer; num2 : real) : real;
begin
   msum := num1 + num2;
end; { msum }

function fsum(num : real; num2 : real) : real;
begin
   fsum := num + num2;
end; { fsum }

function osum(num2 : integer; num1 : real) : real;
begin
   osum := num2 + num1;
end; { osum }

function osum1(num2 : real; num1 : integer) : real;
begin
   osum1 := num2 + num1;
end; { osum }

function onearg(arg : integer) : integer;
begin
   onearg := arg;
end; { onearg }

function noarg: integer;
begin
   noarg := 0;
end;

function noargnoret;
begin
   i := 25;
end; { noargnoret }

BEGIN
   i := 1;
   r := PI;
   
   i := isum(i, 2);
   if i = 3 then
      writeln("OK")
   else
      halt(1);
   
   r := msum(2, 2);
   if r = 4 then
      writeln("OK")
   else
      halt(1);

   r := fsum(5, 2);
   if r = 7 then
      writeln("OK")
   else
      halt(1);

   r := osum(5, 2);
   if r = 7 then
      writeln("OK")
   else
      halt(1);

   r := osum1(5, 2);
   if r = 7 then
      writeln("OK")
   else
      halt(1);
   
   if onearg(5) = 5 then
      writeln("OK")
   else
      halt(1);

   i := noarg;
   if i = 0 then
      writeln("OK")
   else
      halt(1);
   
   if noarg = 0 then
      writeln("OK")
   else
      halt(1);
   
   noargnoret;
   if i = 25 then
      writeln("OK")
   else
      halt(1);


end.
