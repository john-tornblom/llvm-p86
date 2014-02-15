program Assign2Test(input, output);

const
   MIN_B   = false;
   MAX_B   = true;
   MIN_S4  = -8;
   MAX_S4  = 7;
   MIN_U4  = 0;
   MAX_U4  = 15;
   MIN_S8  = -128;
   MAX_S8  = 127;
   MIN_U8  = 0;
   MAX_U8  = 255;
   MIN_S16 = -32768;
   MAX_S16 = 32767;
   MIN_U16 = 0;
   MAX_U16 = 65535;
   MIN_S32 = -2147483648;
   MAX_S32 = 2147483647;
   MIN_U32 = 0;
   MAX_U32 = 4294967295;

type
   T_BOOL    = boolean;
   T_SINT4   = MIN_S4..MAX_S4;
   T_UINT4   = MIN_U4..MAX_U4;
   T_SINT8   = MIN_S8..MAX_S8;
   T_UINT8   = MIN_U8..MAX_U8;
   T_SINT16  = MIN_S16..MAX_S16;
   T_UINT16  = MIN_U16..MAX_U16;
   T_WORD    = word;
   T_INT     = integer;
   T_SINT32  = MIN_S32..MAX_S32;
   T_UINT32  = MIN_U32..MAX_U32;
   T_LONGINT = longint;

var
   b   : T_BOOL;
   u4  : T_UINT4;
   u8  : T_UINT8;
   u16 : T_UINT16;
   u32 : T_UINT32;
   s4  : T_SINT4;
   s8  : T_SINT8;
   s16 : T_SINT16;
   s32 : T_SINT32;
   l   : longint;
   w   : word;
   i   : integer;

procedure Assert(b : boolean);
Begin
   If b Then
      Writeln('OK')
   Else
      Halt(1);
End; { Assert }

begin
   { small bool }
   WriteLn('small bool');
   b := MIN_B;
   Assert(b = MIN_B);
   Assert(b < MAX_B);

   { large bool }
   WriteLn('large bool');
   b := MAX_B;
   Assert(b = MAX_B);
   Assert(b > MIN_B);

   { small u4 }
   WriteLn('small u4');
   u4 := MIN_U4;
   Assert(u4 = 0);
   
   Assert(u4 > MIN_S8);
   Assert(u4 > MIN_S16);
   Assert(u4 > MIN_S32);

   Assert(u4 < MAX_S4);
   Assert(u4 < MAX_S8);
   Assert(u4 < MAX_S16);
   Assert(u4 < MAX_S32);

   Assert(u4 - 1 = -1);
   Assert(u4 + 1 = 1);
   Assert(u4 - 10 = -10);
   Assert(u4 + 10 = 10);
   
   { large u4 }
   WriteLn('large u4');
   u4 := MAX_U4;
   Assert(u4 = 15);
   
   Assert(u4 > MIN_S8);
   Assert(u4 > MIN_S16);
   Assert(u4 > MIN_S32);

   Assert(u4 > MAX_S4);
   Assert(u4 < MAX_S8);
   Assert(u4 < MAX_S16);
   Assert(u4 < MAX_S32);

   Assert(u4 - 1 = 14);
   Assert(u4 + 1 = 16);
   Assert(u4 - 10 = 5);
   Assert(u4 + 10 = 25);

   { small s4 }
   WriteLn('small s4');
   s4 := MIN_S4;
   Assert(s4 = -8);
   
   Assert(s4 > MIN_S8);
   Assert(s4 > MIN_S16);
   Assert(s4 > MIN_S32);

   Assert(s4 < MAX_S4);
   Assert(s4 < MAX_S8);
   Assert(s4 < MAX_S16);
   Assert(s4 < MAX_S32);

   Assert(s4 - 1 = -9);
   Assert(s4 + 1 = -7);
   Assert(s4 - 10 = -18);
   Assert(s4 - 10000000 = -10000008);
   Assert(s4 + 10 = 2);
   Assert(s4 + 10000008 = 10000000);
   
   { large s4 }
   WriteLn('large s4');
   s4 := MAX_S4;
   Assert(s4 = 7);
   
   Assert(s4 > MIN_S8);
   Assert(s4 > MIN_S16);
   Assert(s4 > MIN_S32);

   Assert(s4 = MAX_S4);
   Assert(s4 < MAX_S8);
   Assert(s4 < MAX_S16);
   Assert(s4 < MAX_S32);

   Assert(s4 - 1 = 6);
   Assert(s4 + 1 = 8);
   Assert(s4 - 10 = -3);
   Assert(s4 + 10 = 17);

   { small u8 }
   WriteLn('small u8');
   u8 := MIN_U8;
   Assert(u8 = 0);

   Assert(u8 > MIN_S4);
   Assert(u8 > MIN_S8);
   Assert(u8 > MIN_S16);
   Assert(u8 > MIN_S32);

   Assert(u8 < MAX_S4);
   Assert(u8 < MAX_S8);
   Assert(u8 < MAX_S16);
   Assert(u8 < MAX_S32);

   Assert(u8 - 1 = -1);
   Assert(u8 + 1 = 1);
   Assert(u8 - 10 = -10);
   Assert(u8 + 10 = 10);
   
   { large u8 }
   WriteLn('large u8');
   u8 := MAX_U8;
   Assert(u8 = 255);

   Assert(u8 > MIN_S4);
   Assert(u8 > MIN_S8);
   Assert(u8 > MIN_S16);
   Assert(u8 > MIN_S32);

   Assert(u8 > MAX_S4);
   Assert(u8 > MAX_S8);
   Assert(u8 < MAX_S16);
   Assert(u8 < MAX_S32);

   Assert(u8 - 1 = 254);
   Assert(u8 + 1 = 256);
   Assert(u8 - 10 = 245);
   Assert(u8 + 10 = 265);
   
   { small s8 }
   WriteLn('small s8');
   s8 := MIN_S8;
   Assert(s8 = -128);

   Assert(s8 < MIN_S4);
   Assert(s8 = MIN_S8);
   Assert(s8 > MIN_S16);
   Assert(s8 > MIN_S32);

   Assert(s8 < MAX_S4);
   Assert(s8 < MAX_S8);
   Assert(s8 < MAX_S16);
   Assert(s8 < MAX_S32);

   Assert(s8 - 1 = -129);
   Assert(s8 + 1 = -127);
   Assert(s8 - 10 = -138);
   Assert(s8 + 10 = -118);
   
   { large s8 }
   WriteLn('large s8');
   s8 := MAX_S8;
   Assert(s8 = 127);

   Assert(s8 > MIN_S4);
   Assert(s8 > MIN_S8);
   Assert(s8 > MIN_S16);
   Assert(s8 > MIN_S32);

   Assert(s8 > MAX_S4);
   Assert(s8 = MAX_S8);
   Assert(s8 < MAX_S16);
   Assert(s8 < MAX_S32);

   Assert(s8 - 1 = 126);
   Assert(s8 + 1 = 128);
   Assert(s8 - 10 = 117);
   Assert(s8 + 10 = 137);

   { small u16 }
   WriteLn('small u16');
   u16 := MIN_U16;
   Assert(u16 = 0);

   Assert(u16 > MIN_S4);
   Assert(u16 > MIN_S8);
   Assert(u16 > MIN_S16);
   Assert(u16 > MIN_S32);

   Assert(u16 < MAX_S4);
   Assert(u16 < MAX_S8);
   Assert(u16 < MAX_S16);
   Assert(u16 < MAX_S32);

   Assert(u16 - 1 = -1);
   Assert(u16 + 1 = 1);
   Assert(u16 - 10 = -10);
   Assert(u16 + 10 = 10);
   
   { large u16 }
   WriteLn('large u16');
   u16 := MAX_U16;
   Assert(u16 = 65535);

   Assert(u16 > MIN_S4);
   Assert(u16 > MIN_S8);
   Assert(u16 > MIN_S16);
   Assert(u16 > MIN_S32);

   Assert(u16 > MAX_S4);
   Assert(u16 > MAX_S8);
   Assert(u16 > MAX_S16);
   Assert(u16 < MAX_S32);

   Assert(u16 - 1 = 65534);
   Assert(u16 + 1 = 65536);
   Assert(u16 - 10 = 65525);
   Assert(u16 + 10 = 65545);
   
   { small s16 }
   WriteLn('small s16');
   s16 := MIN_S16;
   Assert(s16 = -32768);

   Assert(s16 < MIN_S4);
   Assert(s16 < MIN_S8);
   Assert(s16 = MIN_S16);
   Assert(s16 > MIN_S32);

   Assert(s16 < MAX_S4);
   Assert(s16 < MAX_S8);
   Assert(s16 < MAX_S16);
   Assert(s16 < MAX_S32);

   Assert(s16 - 1 = 32767);
   Assert(s16 + 1 = -32767);
   Assert(s16 - 10 = 32758);
   Assert(s16 + 10 = -32758);

   { large s16 }
   WriteLn('large s16');
   s16 := MAX_S16;
   Assert(s16 = 32767);

   Assert(s16 > MIN_S4);
   Assert(s16 > MIN_S8);
   Assert(s16 > MIN_S16);
   Assert(s16 > MIN_S32);

   Assert(s16 > MAX_S4);
   Assert(s16 > MAX_S8);
   Assert(s16 = MAX_S16);
   Assert(s16 < MAX_S32);

   Assert(s16 - 1 = 32766);
   Assert(s16 + 1 = -32768);

   Assert(s16 - 10 = 32757);
   Assert(s16 + 10 = -32759);

   { small s32 }
   WriteLn('small s32');
   s32 := MIN_S32;
   Assert(s32 = -2147483648);

   Assert(s32 < MIN_S4);
   Assert(s32 < MIN_S8);
   Assert(s32 < MIN_S16);
   Assert(s32 = MIN_S32);

   Assert(s32 < MAX_S4);
   Assert(s32 < MAX_S8);
   Assert(s32 < MAX_S16);
   Assert(s32 < MAX_S32);

   Assert(s32 - 1 = -2147483649);
   Assert(s32 + 1 = -2147483647);
   Assert(s32 - 10 = -2147483658);
   Assert(s32 + 10 = -2147483638);

   { large s32 }
   WriteLn('large s32');
   s32 := MAX_S32;
   Assert(s32 = 2147483647);

   Assert(s32 > MIN_S4);
   Assert(s32 > MIN_S8);
   Assert(s32 > MIN_S16);
   Assert(s32 > MIN_S32);

   Assert(s32 > MAX_S4);
   Assert(s32 > MAX_S8);
   Assert(s32 > MAX_S16);
   Assert(s32 = MAX_S32);

   Assert(s32 - 1 = 2147483646);
   Assert(s32 + 1 = MIN_S32);

   Assert(s32 - 10 = 2147483637);
   Assert(s32 + 10 = MIN_S32 + 9);

   { small longint }
   WriteLn('small longint');
   l := MIN_S32;
   Assert(l = -2147483648);

   Assert(l < MIN_S4);
   Assert(l < MIN_S8);
   Assert(l < MIN_S16);
   Assert(l = MIN_S32);

   Assert(l < MAX_S4);
   Assert(l < MAX_S8);
   Assert(l < MAX_S16);
   Assert(l < MAX_S32);

   Assert(l - 1 = MAX_S32);
   Assert(l + 1 = -2147483647);
   Assert(l - 10 = MAX_S32 - 9);
   Assert(l + 10 = -2147483638);

   { large longint }
   WriteLn('large longint');
   l := MAX_S32;
   Assert(l = 2147483647);

   Assert(l > MIN_S4);
   Assert(l > MIN_S8);
   Assert(l > MIN_S16);
   Assert(l > MIN_S32);

   Assert(l > MAX_S4);
   Assert(l > MAX_S8);
   Assert(l > MAX_S16);
   Assert(l = MAX_S32);

   Assert(l - 1 = 2147483646);
   Assert(l + 1 = MIN_S32);

   Assert(l - 10 = 2147483637);
   Assert(l + 10 = MIN_S32 + 9);


   { small word }
   WriteLn('small word');
   w := MIN_U16;
   Assert(w = 0);

   Assert(w > MIN_S4);
   Assert(w > MIN_S8);
   Assert(w > MIN_S16);
   Assert(w > MIN_S32);

   Assert(w < MAX_S4);
   Assert(w < MAX_S8);
   Assert(w < MAX_S16);
   Assert(w < MAX_S32);

   Assert(w - 1 = -1);
   Assert(w + 1 = 1);
   Assert(w - 10 = -10);
   Assert(w + 10 = 10);
         
   { large word }
   WriteLn('large word');
   w := MAX_U16;
   Assert(w = 65535);

   Assert(w > MIN_S4);
   Assert(w > MIN_S8);
   Assert(w > MIN_S16);
   Assert(w > MIN_S32);

   Assert(w > MAX_S4);
   Assert(w > MAX_S8);
   Assert(w > MAX_S16);
   Assert(w < MAX_S32);

   Assert(w - 1 = 65534);
   Assert(w + 1 = 65536);
   Assert(w - 10 = 65525);
   Assert(w + 10 = 65545);

   { small integer }
   WriteLn('small integer');
   i := MIN_S16;
   Assert(i = -32768);

   Assert(i < MIN_S4);
   Assert(i < MIN_S8);
   Assert(i = MIN_S16);
   Assert(i > MIN_S32);

   Assert(i < MAX_S4);
   Assert(i < MAX_S8);
   Assert(i < MAX_S16);
   Assert(i < MAX_S32);

   Assert(i - 1 = MAX_S16);
   Assert(i + 1 = -32767);
   Assert(i - 10 = MAX_S16 - 9);
   Assert(i + 10 = -32758);

   { large integer }
   WriteLn('large integer');
   i := MAX_S16;
   Assert(i = 32767);

   Assert(i > MIN_S4);
   Assert(i > MIN_S8);
   Assert(i > MIN_S16);
   Assert(i > MIN_S32);

   Assert(i > MAX_S4);
   Assert(i > MAX_S8);
   Assert(i = MAX_S16);
   Assert(i < MAX_S32);

   Assert(i - 1 = 32766);
   Assert(i + 1 = MIN_S16);

   Assert(i - 10 = 32757);
   Assert(i + 10 = MIN_S16 + 9);

   { small u32 }
   WriteLn('small u32');
   u32 := MIN_U32;
   Assert(u32 = 0);

   Assert(u32 > MIN_S4);
   Assert(u32 > MIN_S8);
   Assert(u32 > MIN_S16);
   Assert(u32 > MIN_S32);

   Assert(u32 < MAX_S4);
   Assert(u32 < MAX_S8);
   Assert(u32 < MAX_S16);
   Assert(u32 < MAX_S32);

   Assert(u32 - 1 = -1);
   Assert(u32 + 1 = 1);
   Assert(u32 - 10 = -10);
   Assert(u32 + 10 = 10);
   
   { large u32 }
   WriteLn('large u32');
   u32 := MAX_U32;
   Assert(u32 = 4294967295);

   Assert(u32 > MIN_S4);
   Assert(u32 > MIN_S8);
   Assert(u32 > MIN_S16);
   Assert(u32 > MIN_S32);

   Assert(u32 > MAX_S4);
   Assert(u32 > MAX_S8);
   Assert(u32 > MAX_S16);
   Assert(u32 > MAX_S32);

   Assert(u32 - 1 = 4294967294);
   Assert(u32 + 1 = 4294967296);
   Assert(u32 - 10 = 4294967285);
   Assert(u32 + 10 = 4294967305);

end.
