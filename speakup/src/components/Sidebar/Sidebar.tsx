import React, { useState } from 'react';
import { 
  Drawer, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon,
  ListItemButton,
  Typography,
  Box,
  IconButton,
  styled
} from '@mui/material';
import { 
  Person, 
  Search, 
  Refresh,
  Menu as MenuIcon
} from '@mui/icons-material';

const drawerWidth = 280;

const StyledDrawer = styled(Drawer)`
  & .MuiDrawer-paper {
    width: ${drawerWidth}px;
    background-color: #f5f5f5;
    color: #333;
    border-right: none;
    padding: 16px;
    transition: width 0.3s ease;
    overflow-x: hidden;

    &.collapsed {
      width: 0;
      padding: 0;
    }
  }
`;

const DrawerHeader = styled(Box)`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
`;

const LogoText = styled(Typography)`
  font-size: 24px;
  font-weight: bold;
  color: #333;
`;

const MenuButton = styled(IconButton)`
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 1400;
  background-color: #f5f5f5;
  
  &:hover {
    background-color: #eee;
  }
`;

const StyledListItem = styled(ListItemButton)`
  border-radius: 8px;
  margin-bottom: 4px;
  padding: 8px 16px;
  
  &:hover {
    background-color: #eee;
  }
`;

const TopActions = styled(Box)`
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
`;

const ActionButton = styled(IconButton)`
  color: #666;
  background-color: white;
  border-radius: 8px;
  padding: 8px;
  
  &:hover {
    background-color: #eee;
  }
`;

const menuItems = [
  { 
    id: 'job-role',
    title: 'Your details',
    description: 'Select your job role',
    icon: <Person />,
    section: 'SETUP'
  },
  { 
    id: 'interview-type',
    title: 'Interview type',
    description: 'Select interview type',
    icon: <Search />,
    section: 'SETUP'
  },
  { 
    id: 'details',
    title: 'Duration',
    description: 'Select duration',
    icon: <Refresh />,
    section: 'SETUP'
  }
];

export const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleDrawer = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      <MenuButton onClick={toggleDrawer}>
        <MenuIcon />
      </MenuButton>

      <StyledDrawer 
        variant="permanent"
        classes={{
          paper: isOpen ? '' : 'collapsed'
        }}
      >
        <DrawerHeader>
          <LogoText>SpeakUp</LogoText>
        </DrawerHeader>

        <TopActions>
          <ActionButton>
            <Search />
          </ActionButton>
          <ActionButton>
            <Refresh />
          </ActionButton>
        </TopActions>
        
        <Typography 
          sx={{ 
            color: '#666',
            fontSize: '14px',
            margin: '16px 0 8px 16px'
          }}
        >
          SETUP
        </Typography>
        
        <List>
          {menuItems.map((item) => (
            <ListItem disablePadding key={item.id}>
              <StyledListItem>
                <ListItemIcon sx={{ color: '#666', minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.title}
                  secondary={item.description}
                  primaryTypographyProps={{
                    variant: 'body1',
                    style: { fontWeight: 500 }
                  }}
                  secondaryTypographyProps={{
                    style: { color: '#666' }
                  }}
                />
              </StyledListItem>
            </ListItem>
          ))}
        </List>
      </StyledDrawer>
    </>
  );
}; 