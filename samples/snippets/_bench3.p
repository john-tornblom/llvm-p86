program ackermann;
const
   NUM = 12;
   
function Ack(M, N : longint) : longint;
begin    
   if M = 0 then Ack := N+1
   else if N = 0 then Ack := Ack(M-1, 1)
   else Ack := Ack(M-1, Ack(M, N-1))
End;

begin
   WriteLn('N = ', NUM);
   WriteLn( 'Ack(3,', NUM, '): ', Ack(3, NUM));
end.