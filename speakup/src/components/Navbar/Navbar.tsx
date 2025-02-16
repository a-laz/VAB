import React from 'react';
import { AppBar, Toolbar, IconButton, Avatar, Box, Typography, styled } from '@mui/material';
import { Notifications, Settings } from '@mui/icons-material';
import { useMediaQuery, useTheme } from '@mui/material';

const StyledAppBar = styled(AppBar)`
  background-color: white;
  color: #333;
  width: 100%;
  z-index: 1300;
  box-shadow: none;
  border-bottom: 1px solid #eee;
`;

const StyledToolbar = styled(Toolbar)`
  @media (max-width: 600px) {
    padding-left: 8px;
    padding-right: 8px;
  }
`;

const LogoContainer = styled(Box)`
  flex-grow: 1;
  display: flex;
  align-items: center;
`;

const Logo = styled(Typography)`
  font-size: 24px;
  font-weight: bold;
  color: #333;
  
  @media (max-width: 600px) {
    font-size: 20px;
  }
`;

const UserInfo = styled(Box)`
  display: flex;
  align-items: center;
  gap: 8px;
  
  @media (max-width: 600px) {
    gap: 4px;
  }
`;

const UserName = styled(Typography)`
  margin-right: 8px;
`;

interface NavbarProps {
  userName?: string;
}

export const Navbar = ({ userName = "Jodi Johnson" }: NavbarProps) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <StyledAppBar position="fixed">
      <StyledToolbar>
        <LogoContainer>
          <Logo>SpeakUp</Logo>
        </LogoContainer>
        
        <UserInfo>
          {!isMobile && (
            <>
              <IconButton color="inherit">
                <Notifications />
              </IconButton>
              <IconButton color="inherit">
                <Settings />
              </IconButton>
              <UserName variant="body1">{userName}</UserName>
            </>
          )}
          <IconButton>
            <Avatar sx={{ width: isMobile ? 28 : 32, height: isMobile ? 28 : 32 }} />
          </IconButton>
        </UserInfo>
      </StyledToolbar>
    </StyledAppBar>
  );
}; 