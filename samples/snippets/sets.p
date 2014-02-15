program SetsTest;

Type
   T_UINT8  = 0..255;
   T_SINT8  = -128..127;
   T_UINT4  = 0..15;
   T_SINT4  = -8..7;
   T_NUMBER = (ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE);

Var	    
   numbers : SET of T_NUMBER;
   n1	   : SET of T_NUMBER;
   n2	   : SET of T_NUMBER;
   u8_ints : SET of T_UINT8;
   u4_ints : SET of T_UINT4;
   num	   : T_NUMBER;
   u8	   : T_UINT8;
   u4,i,j  : T_UINT4;


Procedure Assert(value, expected: Boolean);
Begin
   If value = expected Then
      Writeln('OK')
   Else
      halt(1);
End; { Assert }

begin
   numbers := [];
   Assert(true, numbers = []);
   Assert(false, ONE in numbers);
   Assert(false, TWO in numbers);
   Assert(false, THREE in numbers);
   Assert(false, FOUR in numbers);
   Assert(false, FIVE in numbers);
   Assert(false, SIX in numbers);
   Assert(false, SEVEN in numbers);
   Assert(false, EIGHT in numbers);
   Assert(false, NINE in numbers);
      
   numbers := [ONE..NINE];
   Assert(true, ONE in numbers);
   Assert(true, TWO in numbers);
   Assert(true, THREE in numbers);
   Assert(true, FOUR in numbers);
   Assert(true, FIVE in numbers);
   Assert(true, SIX in numbers);
   Assert(true, SEVEN in numbers);
   Assert(true, EIGHT in numbers);
   Assert(true, NINE in numbers);

   numbers := [ONE];
   Assert(true, ONE in numbers);
   Assert(false, TWO in numbers);
   Assert(false, THREE in numbers);
   Assert(false, FOUR in numbers);
   Assert(false, FIVE in numbers);
   Assert(false, SIX in numbers);
   Assert(false, SEVEN in numbers);
   Assert(false, EIGHT in numbers);
   Assert(false, NINE in numbers);

   numbers := [NINE];
   Assert(false, ONE in numbers);
   Assert(false, TWO in numbers);
   Assert(false, THREE in numbers);
   Assert(false, FOUR in numbers);
   Assert(false, FIVE in numbers);
   Assert(false, SIX in numbers);
   Assert(false, SEVEN in numbers);
   Assert(false, EIGHT in numbers);
   Assert(true, NINE in numbers);

   numbers := [ONE, FIVE, NINE];
   Assert(true, ONE in numbers);
   Assert(false, TWO in numbers);
   Assert(false, THREE in numbers);
   Assert(false, FOUR in numbers);
   Assert(true, FIVE in numbers);
   Assert(false, SIX in numbers);
   Assert(false, SEVEN in numbers);
   Assert(false, EIGHT in numbers);
   Assert(true, NINE in numbers);

   n1 := [ONE, FIVE, NINE];
   n2 := [ONE, NINE];
   numbers := n1 * n2;
   
   Assert(true, ONE in numbers);
   Assert(false, TWO in numbers);
   Assert(false, THREE in numbers);
   Assert(false, FOUR in numbers);
   Assert(false, FIVE in numbers);
   Assert(false, SIX in numbers);
   Assert(false, SEVEN in numbers);
   Assert(false, EIGHT in numbers);
   Assert(true, NINE in numbers);

   n1 := [ONE, FIVE, TWO];
   n2 := [ONE, NINE, SEVEN, TWO];
   numbers := n1 + n2;
   
   Assert(true, ONE in numbers);
   Assert(true, TWO in numbers);
   Assert(false, THREE in numbers);
   Assert(false, FOUR in numbers);
   Assert(true, FIVE in numbers);
   Assert(false, SIX in numbers);
   Assert(true, SEVEN in numbers);
   Assert(false, EIGHT in numbers);
   Assert(true, NINE in numbers);

   n1 := [ONE, FIVE, NINE];
   n2 := [ONE, NINE];
   numbers := n1 - n2;
   
   Assert(false, ONE in numbers);
   Assert(false, TWO in numbers);
   Assert(false, THREE in numbers);
   Assert(false, FOUR in numbers);
   Assert(true, FIVE in numbers);
   Assert(false, SIX in numbers);
   Assert(false, SEVEN in numbers);
   Assert(false, EIGHT in numbers);
   Assert(false, NINE in numbers);

 
   u4 := 0;
   Assert(false, u4 in [1,2,3]);

   u4 := 1;
   Assert(true, u4 in [1,2,3]);

   u4 := 0;
   Assert(true, u4 in [0]);

   u4 := 1;
   Assert(false, u4 in []);

   u4 := 1;
   Assert(true, 1 in [u4]);
   
   u4 := 1;
   Assert(true, u4 in [1, 2, 3]);

   for i := 0 to 15 do
   begin
      u4_ints := [i];
      Assert(true, i in u4_ints);
   end;
   
   for i := 0 to 15 do
   begin
      u4_ints := [];
      
      for j := 0 to i do
      begin
	 u4_ints := u4_ints + [j];
      end;

      Assert(true, i in u4_ints);
      Assert(false, (i+1) in u4_ints);
   end;
   u8_ints := [];
   Assert(true, (i-1) in u4_ints); 
   Assert(true, (i-1) in u4_ints + u8_ints);

   Assert(true, 4 in [1,2] + [4, 8]);


   Assert(true, [1,2] = [1] + [2]); 
end.
