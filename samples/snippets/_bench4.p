program fibo;
const
   NUM = 44;

function fib(N : longint) : longint;
begin
   if N < 2 then fib := 1
   else fib := fib(N-2) + fib(N-1);
end;

begin
   WriteLn('N = ', NUM);
   WriteLn(fib(NUM));
end.