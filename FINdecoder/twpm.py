int TPWM_Unpack()
// Unpacks data that is compressed with Turbo Packer
// TPWM struct musst be set
{
    unsigned char b1;
    unsigned char b2;
    unsigned char packbyte;
    char          bit;
    unsigned int  i;
    unsigned int  inofs;
    unsigned int  outofs;
    unsigned int  distance;
    unsigned int  length;

    outofs = 0;
    inofs = 0;


    while (outofs < TPWM.unpacked_size)
    {
        packbyte = TPWM.packed_data[inofs];
        inofs++;

        for (bit = 7; bit >= 0; bit--)
        {
            if (getbit(packbyte, bit) = 1)
            {
                b1 = TPWM.packed_data[inofs];
                inofs++;
                b2 = TPWM.packed_data[inofs];
                inofs++;

                distance = (unsigned int)((b1 & 0xF0) << 4) | b2;
                if (distance > outofs) break;

                length = (unsigned int)(b1 & 0x0F) + 3;

                for (i = 0; i <= (length - 1); i++)
                {
                    if (outofs < TPWM.unpacked_size)
                    {
                        TPWM.unpacked_data[outofs] = TPWM.unpacked_data[(outofs - distance)];
                        outofs++;
                    }
                    else
                        break;
                }
            }
            else
            {
                if ((outofs < TPWM.unpacked_size) && (inofs < TPWM.packed_size))
                {
                  TPWM.unpacked_data[outofs] = TPWM.packed_data[inofs];
                  inofs++;
                  outofs++;
                }
                else
                  break;

            }
        }

        if (outofs >= TPWM.unpacked_size)
            break;

    }


    if (outofs == TPWM.unpacked_size)
        return 0;
    else
        return -1;
}







#                1         2             3         4        5         6         7         8         9         10        11                   12         13         14         15         
uncomprString = "0x50 0xff 0x8e 0xff     0x37 0xff 0x0 0xff 0x38 0xff 0x39 0xff 0x38 0xff 0x38 0xff 0x38 0xff 0x39 0xff 0x38 0xff            0x31 0xff  0x50 0xff  0x50 0xff  0x38 0xff"
compressed    = "0x50 0xff 0x8e 0xff 0x1 0x37 0xff 0x0 0xff 0x38 0xff 0x39                                      0x0 0x4 0xc4 0x1 0x2 0x1 0x8 0x31 0xff  0x50 0x0 0x2          0x38 0xff 0x0"




rawData = open("00.FIN", "rb").read()
packedData = rawData[8:]
sizeOfPackedData = int.from_bytes(rawData[4:8], byteorder='little')


print(len(rawData))
print(len(packedData))
print(sizeOfPackedData)

print(uncomprString)
for b in rawData[13:13 + 27]:
        print(hex(b), end=" ")



# open file
# pf = fopen(partlib_filename, "rb");

# (Unpack_file(pf)



##int Unpack_file(FILE* f)
##// Unpacks a file compressed with Turbo Packer
##{
##	size_t 				IO_result;
##	int				result;
##
##	fseek(f, 0, SEEK_END);	//Get file size
##	TPWM.packed_size = ftell(f) - 8;
##	rewind(f);
##	fseek(f, 4, SEEK_SET);
##
##	IO_result = fread(&TPWM.unpacked_size, sizeof(TPWM.unpacked_size), 1, f); //Read unpacked size
##
##	if (IO_result != 1) //Read Error?
##	{
##		fclose(f);
##		return -2;
##	}
##	TPWM.packed_data = (byte huge*)farmalloc(TPWM.packed_size);
##
##	if (TPWM.packed_data == NULL)
##	{
##		fclose(f);
##		return -4; //Reserve memory buffer for packed data failed
##	}
##
##	_fmemset((byte huge*)TPWM.packed_data, 0, TPWM.packed_size);  //Clear it;
##
##	if (Read_Chunk(f,TPWM.packed_size,TPWM.packed_data) != 0)
##	{
##		farfree(TPWM.packed_data);
##		fclose(f);
##		return -2;
##	}
##
##	fclose(f);
##
##	TPWM.unpacked_data = (byte huge*) farmalloc(TPWM.unpacked_size);
##
##	if (TPWM.unpacked_data == NULL) //Reserve memory buffer for unpacked data
##	{
##		farfree(TPWM.packed_data);
##		return -4;
##	}
##	_fmemset((byte huge*) TPWM.unpacked_data, 0, TPWM.unpacked_size);  //Clear it;
##
##
##	if (TPWM_Unpack() != 0)
##	{
##		farfree(TPWM.packed_data);
##		farfree(TPWM.unpacked_data);
##		return -5;	//Decompression failed
##	}
##
##	farfree(TPWM.packed_data); //Free buffer for packed data - we don't need it anymore
##	return 0;
##}
















