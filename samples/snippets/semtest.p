program semtest1;

{ all the stuff below should work }

var
   a	 : integer;
   b	 : integer;
   x	 : real;
   y	 : real;
   i_arr : array[0..10] of integer;

procedure index(i : integer);
var
   j : integer;
begin
   j := 10;
   while (j > 0) do
   begin
      i_arr[1+i-1] := j;
      i_arr[i_arr[i]] := i_arr[i] - j;
      j := j - 1;
   end;
end;

function max(a : integer; x : real) : integer;
begin
   if (a > b) then
      max := a
   else if (b > a) then
      max := b
   else
      max := a;
end; { max }

procedure nasty(i : integer; j : integer; x : real; y : real);
var
   nasty_1 : integer;
   nasty_2 : array[0..10] of integer;
        
   procedure do_zero;
      const
	 OREZ = 48;
	 ZERO = OREZ;
      var	      
	 z : integer;
      begin
	 z := ZERO;
	 write(z);
      end; { do_zero }
begin
   i := j;
   x := -i;
   i := i div j;
   x := i/j;
   do_zero;
   if ((x = i) and (i < j)) then
   begin
      i := max(i, y);
      j := 0;
      x := 0;
      y := 0;
   end;
end; { nasty }

begin
   a := 1; b := 2; x := 1; y := 3.14;
   index(a);
   nasty(1 div 2, 5, 1/2, 8.0+7);
end.
