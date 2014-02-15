program NestedFunctionTest3;
const
   s = 'OK';

function fib(n : integer) : integer;

   function fib_helper : integer;
   begin
      if n < 2 then
	 fib_helper := 1
      else
	 fib_helper := fib(n-2) + fib(n-1);
   end; { fib_helper }

begin
   fib := fib_helper;
end; { fib }

begin
   if fib(10) = 89 then
      writeln(s)
   else
      halt(1);
end.
